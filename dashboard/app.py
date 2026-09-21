"""Main Entrypoint for Ride-Sharing Operational Intelligence Platform."""

import sys
from pathlib import Path

# Ensure workspace root is on sys.path for direct streamlit execution
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import streamlit as st

from dashboard.components.kpi_card import render_stat_strip
from dashboard.utils.db import fetch_city_summary, fetch_global_summary
from dashboard.utils.styling import apply_theme
from src.ingestion.pipeline import pipeline

# Configure page layout
st.set_page_config(
    page_title="Operational Intelligence | Mobility Ops",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply global CSS styling tokens
apply_theme()

# Sidebar
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 6px 0 16px 0;">
            <div style="font-size: 0.9rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em;">
                Mobility Operations
            </div>
            <div style="font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 2px;">
                Operational Intelligence Console
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("### Telemetry Controls")
    if st.button("Rebuild Analytics Marts", width="stretch"):
        with st.spinner("Executing analytical data marts..."):
            pipeline.run(force_regenerate=True)
            st.cache_data.clear()
            st.success("Analytics marts updated.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="briefing-card">
            <strong>System Focus:</strong><br>
            Automated discovery of city-level driver acceptance, rider cancellation, and surge behaviors degrading rider experience during high-demand strain.
        </div>
        """,
        unsafe_allow_html=True,
    )

# Top Application Header Bar
st.markdown(
    """
    <div class="app-header-strip">
        <div class="app-brand">
            <span class="app-brand-title">Ride-Sharing Operational Intelligence</span>
            <span class="app-brand-badge">Engine v1.0</span>
        </div>
        <div style="display: flex; gap: 14px; align-items: center; font-size: 0.75rem; color: var(--text-muted);">
            <span>Engine: <strong style="color: var(--text-primary);">DuckDB In-Process OLAP</strong></span>
            <span>Status: <span class="status-pill status-healthy"><span class="status-dot"></span>Online</span></span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Fetch Global Summary Metrics
summary, lat_ms = fetch_global_summary()
city_summary_df, _ = fetch_city_summary()

if summary:
    total_req = int(summary.get("total_requests", 0))
    hd_req = int(summary.get("high_demand_requests", 0))
    hd_share = summary.get("high_demand_share_pct", 0)

    norm_acc = summary.get("global_normal_acceptance", 0)
    hd_acc = summary.get("global_high_demand_acceptance", 0)
    acc_delta = hd_acc - norm_acc

    norm_canc = summary.get("global_normal_cancellation", 0)
    hd_canc = summary.get("global_high_demand_cancellation", 0)
    canc_delta = hd_canc - norm_canc

    norm_surge = summary.get("global_normal_surge", 1.0)
    hd_surge = summary.get("global_high_demand_surge", 1.0)
    surge_delta = hd_surge - norm_surge

    crit_count = int(summary.get("critical_cities_count", 0))
    watch_count = int(summary.get("watch_cities_count", 0))

    # Render Executive Stat Strip
    render_stat_strip(
        [
            {
                "title": "Total Dispatch Volume",
                "value": f"{total_req:,}",
                "sub_text": f"{hd_req:,} peak ({hd_share}%)",
                "delta_class": "delta-neutral",
            },
            {
                "title": "Driver Acceptance (Peak)",
                "value": f"{hd_acc:.1f}%",
                "sub_text": f"{acc_delta:+.1f} pp vs baseline ({norm_acc:.1f}%)",
                "delta_class": "delta-bad" if acc_delta < -10 else "delta-neutral",
            },
            {
                "title": "Rider Cancellation (Peak)",
                "value": f"{hd_canc:.1f}%",
                "sub_text": f"+{canc_delta:.1f} pp vs baseline ({norm_canc:.1f}%)",
                "delta_class": "delta-bad" if canc_delta > 5 else "delta-good",
            },
            {
                "title": "Average Surge Multiplier",
                "value": f"{hd_surge:.2f}x",
                "sub_text": f"+{surge_delta:.2f}x vs baseline ({norm_surge:.2f}x)",
                "delta_class": "delta-neutral",
            },
            {
                "title": "Market Risk Posture",
                "value": f"{crit_count} Critical",
                "sub_text": f"{watch_count} on active watch",
                "delta_class": "delta-bad" if crit_count > 0 else "delta-good",
            },
        ]
    )

# Main Operational Grid: 2 Column Layout
col_left, col_right = st.columns([3, 2])

with col_left:
    st.markdown("### Market Risk & Capacity Posture")
    st.caption("City-by-city breakdown of peak supply-demand divergence and consistency.")

    if not city_summary_df.empty:
        overview_table = city_summary_df[
            [
                "city",
                "operational_risk_status",
                "high_demand_requests",
                "high_demand_acceptance_pct",
                "acceptance_delta_pp",
                "high_demand_cancellation_pct",
                "cancellation_delta_pp",
                "high_demand_avg_surge",
                "consistency_pct",
            ]
        ].rename(
            columns={
                "city": "Metro",
                "operational_risk_status": "Risk Level",
                "high_demand_requests": "Peak Volume",
                "high_demand_acceptance_pct": "Peak Acceptance",
                "acceptance_delta_pp": "Acceptance Delta",
                "high_demand_cancellation_pct": "Peak Cancellation",
                "cancellation_delta_pp": "Cancellation Delta",
                "high_demand_avg_surge": "Peak Surge",
                "consistency_pct": "Consistency",
            }
        )

        st.dataframe(overview_table, width="stretch", hide_index=True)

with col_right:
    st.markdown("### Analytical Navigation")
    st.caption("Direct access to specialized investigation modules.")

    st.markdown(
        """
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div class="briefing-card">
                <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted);">Page 1</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-top: 2px;">Executive Overview & Risk Matrix</div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">
                    Interactive 4D quadrant mapping (Acceptance vs. Cancellation vs. Surge vs. Volume) and prioritized action alerts.
                </div>
            </div>
            <div class="briefing-card">
                <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted);">Page 2</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-top: 2px;">City Intelligence & Timelines</div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">
                    Individual metropolitan deep-dives, synchronized hourly timelines, and peak concentration distributions.
                </div>
            </div>
            <div class="briefing-card">
                <div style="font-size: 0.72rem; font-weight: 600; text-transform: uppercase; color: var(--text-muted);">Pages 3 - 5</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin-top: 2px;">Diagnostics, Correlations & Health</div>
                <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">
                    High-demand P85 threshold methodology, Pearson/Spearman correlation matrices, deterministic root cause reports, and data quality audits.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption(f"SQL Pushdown Aggregation Latency: {lat_ms:.2f} ms | In-Process Columnar Storage")
