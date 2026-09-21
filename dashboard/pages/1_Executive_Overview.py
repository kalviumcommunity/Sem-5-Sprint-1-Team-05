"""Page 1: Executive Overview & City Risk Matrix."""

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.components.alerts_banner import render_operational_alerts
from dashboard.components.kpi_card import render_stat_strip
from dashboard.utils.db import (
    fetch_city_summary,
    fetch_global_summary,
    fetch_risk_matrix_data,
    fetch_top_alerts,
)
from dashboard.utils.styling import apply_theme, format_plotly_figure

st.set_page_config(page_title="Executive Overview | Mobility Ops", layout="wide")
apply_theme()

st.title("Executive Overview")
st.caption("Cross-market operational posture, capacity strain, and high-demand risk segmentation.")

summary, sum_lat = fetch_global_summary()
risk_df, r_lat = fetch_risk_matrix_data()
alerts_df, a_lat = fetch_top_alerts(limit=5)
full_summary_df, f_lat = fetch_city_summary()

if summary:
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

    render_stat_strip(
        [
            {
                "title": "Peak Volume Analyzed",
                "value": f"{hd_req:,}",
                "sub_text": f"{hd_share}% of total dispatch volume",
                "delta_class": "delta-neutral",
            },
            {
                "title": "Peak Driver Acceptance",
                "value": f"{hd_acc:.1f}%",
                "sub_text": f"{acc_delta:+.1f} pp vs baseline ({norm_acc:.1f}%)",
                "delta_class": "delta-bad" if acc_delta < -10 else "delta-neutral",
            },
            {
                "title": "Peak Rider Cancellation",
                "value": f"{hd_canc:.1f}%",
                "sub_text": f"+{canc_delta:.1f} pp vs baseline ({norm_canc:.1f}%)",
                "delta_class": "delta-bad" if canc_delta > 5 else "delta-good",
            },
            {
                "title": "Peak Surge Multiplier",
                "value": f"{hd_surge:.2f}x",
                "sub_text": f"+{surge_delta:.2f}x vs baseline ({norm_surge:.2f}x)",
                "delta_class": "delta-neutral",
            },
        ]
    )

st.markdown("---")

# 2. City Operational Risk Matrix
st.subheader("City Operational Risk Matrix")
st.caption(
    "Mapping driver supply willingness (Acceptance Rate) against rider cancellation friction. "
    "Upper-left quadrant defines high-risk capacity deficits."
)

if not risk_df.empty:
    fig = px.scatter(
        risk_df,
        x="driver_acceptance_pct",
        y="rider_cancellation_pct",
        size="demand_volume",
        color="operational_risk_status",
        hover_name="city",
        text="city",
        color_discrete_map={"CRITICAL": "#f43f5e", "WATCH": "#f59e0b", "HEALTHY": "#5D6B2E"},
        custom_data=[
            "surge_multiplier",
            "consistency_pct",
            "cancellation_delta_pp",
            "acceptance_delta_pp",
        ],
        labels={
            "driver_acceptance_pct": "High-Demand Driver Acceptance Rate (%)",
            "rider_cancellation_pct": "High-Demand Rider Cancellation Rate (%)",
            "demand_volume": "Peak Volume",
            "operational_risk_status": "Risk Classification",
        },
    )

    fig.update_traces(
        textposition="top center",
        marker={
            "sizemode": "area",
            "sizeref": 2.0 * max(risk_df["demand_volume"]) / (36.0**2),
            "line": {"width": 1, "color": "#D4C9B0"},
        },
        hovertemplate="<b>%{hovertext}</b><br><br>"
        + "Driver Acceptance: %{x:.1f}% (Delta %{customdata[3]:+.1f} pp)<br>"
        + "Rider Cancellation: %{y:.1f}% (Delta %{customdata[2]:+.1f} pp)<br>"
        + "Avg Surge: %{customdata[0]:.2f}x<br>"
        + "Consistency: %{customdata[1]:.1f}%<br>"
        + "<extra></extra>",
    )

    fig.add_hline(
        y=12.0,
        line_dash="dot",
        line_color="#D4C9B0",
        annotation_text="High Cancellation Benchmark (12%)",
        annotation_font_size=10,
        annotation_font_color="#8A7E72",
    )
    fig.add_vline(
        x=75.0,
        line_dash="dot",
        line_color="#D4C9B0",
        annotation_text="Acceptance Benchmark (75%)",
        annotation_font_size=10,
        annotation_font_color="#8A7E72",
    )

    format_plotly_figure(fig, height=480)
    st.plotly_chart(fig, width="stretch")

# 3. Operational Alerts
st.markdown("---")
render_operational_alerts(alerts_df)

# 4. Summary Table
st.markdown("---")
with st.expander("Metropolitan High-Demand Performance Summary Table", expanded=False):
    display_df = full_summary_df[
        [
            "city",
            "operational_risk_status",
            "total_requests_all",
            "high_demand_requests",
            "normal_acceptance_pct",
            "high_demand_acceptance_pct",
            "acceptance_delta_pp",
            "normal_cancellation_pct",
            "high_demand_cancellation_pct",
            "cancellation_delta_pp",
            "normal_avg_surge",
            "high_demand_avg_surge",
            "surge_delta",
            "degraded_hd_periods",
            "total_hd_periods",
            "consistency_pct",
        ]
    ].rename(
        columns={
            "city": "Metro",
            "operational_risk_status": "Risk Level",
            "total_requests_all": "Total Volume",
            "high_demand_requests": "Peak Volume",
            "normal_acceptance_pct": "Norm Acc %",
            "high_demand_acceptance_pct": "Peak Acc %",
            "acceptance_delta_pp": "Delta Acc (pp)",
            "normal_cancellation_pct": "Norm Canc %",
            "high_demand_cancellation_pct": "Peak Canc %",
            "cancellation_delta_pp": "Delta Canc (pp)",
            "normal_avg_surge": "Norm Surge",
            "high_demand_avg_surge": "Peak Surge",
            "surge_delta": "Delta Surge",
            "degraded_hd_periods": "Degraded Windows",
            "total_hd_periods": "Total Peak Windows",
            "consistency_pct": "Consistency %",
        }
    )
    st.dataframe(display_df, width="stretch", hide_index=True)

st.caption(f"SQL Query Latency: {r_lat + sum_lat:.2f} ms")
