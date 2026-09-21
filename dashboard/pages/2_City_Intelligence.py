"""Page 2: Metropolitan Market Intelligence & Timelines."""

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.components.kpi_card import render_stat_strip
from dashboard.utils.db import fetch_city_summary, fetch_city_trends
from dashboard.utils.styling import apply_theme, format_plotly_figure

st.set_page_config(page_title="City Intelligence | Mobility Ops", layout="wide")
apply_theme()

st.title("Metropolitan Intelligence")
st.caption("Hourly telemetry, supply elasticity, and peak period degradation timelines.")

city_summary_df, _ = fetch_city_summary()
city_list = (
    city_summary_df["city"].tolist()
    if not city_summary_df.empty
    else ["Mumbai", "Delhi", "Bengaluru"]
)

# City Selector in clean header
c_sel1, c_sel2 = st.columns([2, 4])
with c_sel1:
    selected_city = st.selectbox("Select Operating Metro:", options=city_list, index=0)

selected_city_data = (
    city_summary_df[city_summary_df["city"] == selected_city].iloc[0]
    if not city_summary_df[city_summary_df["city"] == selected_city].empty
    else None
)

if selected_city_data is not None:
    norm_acc = selected_city_data["normal_acceptance_pct"]
    hd_acc = selected_city_data["high_demand_acceptance_pct"]
    acc_delta = selected_city_data["acceptance_delta_pp"]

    norm_canc = selected_city_data["normal_cancellation_pct"]
    hd_canc = selected_city_data["high_demand_cancellation_pct"]
    canc_delta = selected_city_data["cancellation_delta_pp"]

    norm_surge = selected_city_data["normal_avg_surge"]
    hd_surge = selected_city_data["high_demand_avg_surge"]
    surge_delta = selected_city_data["surge_delta"]

    risk_status = selected_city_data["operational_risk_status"]
    consistency = selected_city_data["consistency_pct"]
    total_req = int(selected_city_data["total_requests_all"])
    hd_req = int(selected_city_data["high_demand_requests"])

    render_stat_strip(
        [
            {
                "title": f"{selected_city} Risk Status",
                "value": risk_status,
                "sub_text": f"Degradation Consistency: {consistency:.1f}%",
                "delta_class": "delta-bad"
                if risk_status == "CRITICAL"
                else ("delta-neutral" if risk_status == "WATCH" else "delta-good"),
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
                "title": "Surge Multiplier (Peak)",
                "value": f"{hd_surge:.2f}x",
                "sub_text": f"+{surge_delta:.2f}x vs baseline ({norm_surge:.2f}x)",
                "delta_class": "delta-neutral",
            },
            {
                "title": "Volume Distribution",
                "value": f"{total_req:,}",
                "sub_text": f"{hd_req:,} peak requests",
                "delta_class": "delta-neutral",
            },
        ]
    )

# 2. Hourly Metrics Timeline
st.markdown("---")
st.subheader("Hourly Operational Timeline")
st.caption(
    "Synchronized hourly trends across driver acceptance, rider cancellation, surge pricing, and request volumes."
)

trends_df, t_lat = fetch_city_trends(selected_city)

if not trends_df.empty:
    fig = go.Figure()

    # Driver Acceptance
    fig.add_trace(
        go.Scatter(
            x=trends_df["date_hour_bucket"],
            y=trends_df["acceptance_rate_pct"],
            name="Driver Acceptance (%)",
            line={"color": "#5D6B2E", "width": 2},
            yaxis="y1",
        )
    )

    # Rider Cancellation
    fig.add_trace(
        go.Scatter(
            x=trends_df["date_hour_bucket"],
            y=trends_df["cancellation_rate_pct"],
            name="Rider Cancellation (%)",
            line={"color": "#f43f5e", "width": 2},
            yaxis="y1",
        )
    )

    # Surge Multiplier
    fig.add_trace(
        go.Scatter(
            x=trends_df["date_hour_bucket"],
            y=trends_df["avg_surge"],
            name="Surge Multiplier",
            line={"color": "#f59e0b", "width": 1.5, "dash": "dot"},
            yaxis="y2",
        )
    )

    # High Demand Windows Shading
    hd_windows = trends_df[trends_df["is_high_demand"] == 1]
    for _, row in hd_windows.iterrows():
        fig.add_vrect(
            x0=row["date_hour_bucket"],
            x1=row["date_hour_bucket"],
            fillcolor="#6366f1",
            opacity=0.08,
            layer="below",
            line_width=0,
        )

    fig.update_layout(
        yaxis={"title": "Rate (%)", "range": [0, 100]},
        yaxis2={
            "title": "Surge (x)",
            "overlaying": "y",
            "side": "right",
            "range": [1.0, 3.5],
            "showgrid": False,
        },
        hovermode="x unified",
    )

    format_plotly_figure(fig, height=380)
    st.plotly_chart(fig, width="stretch")

# 3. Peak Hour Concentration Analysis
st.markdown("---")
st.subheader("Hourly Profile & Regime Breakdown")
c_vol1, c_vol2 = st.columns(2)

with c_vol1:
    have_counts = "cancelled_requests" in trends_df.columns and "total_requests" in trends_df.columns
    if have_counts and not trends_df.empty:
        hourly_agg = (
            trends_df.groupby("hour_of_day")[["total_requests", "cancelled_requests"]]
            .mean()
            .reset_index()
        )
        fig_hour = px.bar(
            hourly_agg,
            x="hour_of_day",
            y=["total_requests", "cancelled_requests"],
            barmode="overlay",
            labels={"hour_of_day": "Hour of Day (0-23)", "value": "Mean Volume"},
            color_discrete_map={"total_requests": "#5D6B2E", "cancelled_requests": "#B8471E"},
        )
        format_plotly_figure(fig_hour, height=320, title="Mean Hourly Volume vs. Cancellations")
        st.plotly_chart(fig_hour, width="stretch")
    elif not trends_df.empty:
        # Fallback: hourly cancellation rate profile
        hourly_agg = (
            trends_df.groupby("hour_of_day")[["cancellation_rate_pct", "acceptance_rate_pct"]]
            .mean()
            .reset_index()
        )
        fig_hour = px.line(
            hourly_agg,
            x="hour_of_day",
            y=["cancellation_rate_pct", "acceptance_rate_pct"],
            labels={"hour_of_day": "Hour of Day (0-23)", "value": "Mean Rate (%)"},
            color_discrete_map={"cancellation_rate_pct": "#B8471E", "acceptance_rate_pct": "#5D6B2E"},
        )
        format_plotly_figure(fig_hour, height=320, title="Hourly Cancellation & Acceptance Rates")
        st.plotly_chart(fig_hour, width="stretch")

with c_vol2:
    fig_scatter = px.scatter(
        trends_df,
        x="acceptance_rate_pct",
        y="cancellation_rate_pct",
        color="is_high_demand",
        color_discrete_map={0: "#2E6B8A", 1: "#B8471E"},
        title="Driver Acceptance vs. Rider Cancellation by Regime",
        labels={
            "acceptance_rate_pct": "Driver Acceptance (%)",
            "cancellation_rate_pct": "Rider Cancellation (%)",
            "is_high_demand": "High Demand (1=Yes)",
        },
    )
    format_plotly_figure(
        fig_scatter, height=320, title="Driver Acceptance vs. Rider Cancellation by Regime"
    )
    st.plotly_chart(fig_scatter, width="stretch")
