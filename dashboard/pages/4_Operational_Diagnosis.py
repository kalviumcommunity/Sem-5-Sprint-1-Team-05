"""Page 4: Operational Diagnosis, Root Cause Analysis & Anomaly Log."""
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import streamlit as st

from dashboard.components.kpi_card import render_stat_strip
from dashboard.utils.db import fetch_anomalies, fetch_city_summary
from dashboard.utils.styling import apply_theme
from src.analytics.diagnosis import diagnosis_engine

st.set_page_config(page_title="Operational Diagnosis | Mobility Ops", layout="wide")
apply_theme()

st.title("Operational Diagnosis & Root Cause Audit")
st.caption("Evidence-backed deterministic causal breakdowns and statistical anomaly detection logs.")

city_summary_df, _ = fetch_city_summary()
city_list = city_summary_df["city"].tolist() if not city_summary_df.empty else ["Mumbai"]

# 1. City Diagnosis Panel
st.subheader("Metropolitan Root Cause Audit")
selected_city = st.selectbox("Select Target Metro for Audit:", options=city_list, index=0)

target_row = city_summary_df[city_summary_df["city"] == selected_city]

if not target_row.empty:
    diag = diagnosis_engine.generate_city_diagnosis(target_row.iloc[0].to_dict())

    # Extract flat metrics from nested metrics_breakdown
    risk_status = diag.get("risk_status", "HEALTHY")
    m = diag.get("metrics_breakdown", {})
    acc = m.get("acceptance", {})
    canc = m.get("cancellation", {})
    surge = m.get("surge", {})
    cons = m.get("consistency", {})

    acc_delta = acc.get("delta_pp", 0.0)
    canc_delta = canc.get("delta_pp", 0.0)
    surge_delta = surge.get("delta", 0.0)
    consistency_pct = cons.get("pct", 0.0)

    render_stat_strip([
        {
            "title": "Audit Risk Classification",
            "value": risk_status,
            "sub_text": f"Consistency: {consistency_pct:.1f}%",
            "delta_class": "delta-bad" if risk_status == "CRITICAL" else ("delta-neutral" if risk_status == "WATCH" else "delta-good"),
        },
        {
            "title": "Acceptance Delta",
            "value": f"{acc_delta:+.1f} pp",
            "sub_text": f"High-Demand {acc.get('high_demand', 0):.1f}% vs Baseline {acc.get('baseline', 0):.1f}%",
            "delta_class": "delta-bad" if acc_delta < -10 else "delta-neutral",
        },
        {
            "title": "Cancellation Delta",
            "value": f"{canc_delta:+.1f} pp",
            "sub_text": f"High-Demand {canc.get('high_demand', 0):.1f}% vs Baseline {canc.get('baseline', 0):.1f}%",
            "delta_class": "delta-bad" if canc_delta > 5 else "delta-good",
        },
        {
            "title": "Surge Delta",
            "value": f"{surge_delta:+.2f}x",
            "sub_text": f"Peak {surge.get('high_demand', 1):.2f}x vs Baseline {surge.get('baseline', 1):.2f}x",
            "delta_class": "delta-neutral",
        },
    ])

    # Diagnosis Findings
    action_text = diag.get("action_recommendation", "")
    dominant_change = diag.get("dominant_change", "")

    st.markdown(
        f"""
        <div class="briefing-card">
            <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #818cf8; letter-spacing: 0.05em; margin-bottom: 6px;">
                Diagnostic Assessment: {selected_city} &mdash; Primary Driver: {dominant_change}
            </div>
            <div class="briefing-body">
                {diag['narrative']}
            </div>
            <div class="briefing-action">
                <strong>Recommended Operational Fix:</strong> {action_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 2. Statistical Anomaly Event Log
st.markdown("---")
st.subheader("Statistical Anomaly Incident Log")
st.caption("Hourly periods where cancellation rate Z-Score >= 2.0 or surge multiplier >= 2.20x.")

anomalies_df, ano_lat = fetch_anomalies()

if not anomalies_df.empty:
    st.dataframe(
        anomalies_df[[
            "city",
            "date_hour_bucket",
            "cancellation_rate_pct",
            "cancellation_z_score",
            "acceptance_rate_pct",
            "avg_surge",
            "total_requests",
            "anomaly_severity",
        ]].rename(
            columns={
                "city": "Metro",
                "date_hour_bucket": "Timestamp",
                "cancellation_rate_pct": "Cancellation Rate",
                "cancellation_z_score": "Z-Score",
                "acceptance_rate_pct": "Acceptance Rate",
                "avg_surge": "Surge",
                "total_requests": "Volume",
                "anomaly_severity": "Severity",
            }
        ),
        hide_index=True,
        width="stretch",
    )
else:
    st.info("No statistical operational anomalies detected in the current analytical window.")

st.caption(f"Anomaly Audit Latency: {ano_lat:.2f} ms")
