"""Page 3: High-Demand Identification & Statistical Methodology."""

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

import plotly.express as px
import streamlit as st

from dashboard.utils.db import fetch_city_summary, fetch_city_trends, fetch_correlation_data
from dashboard.utils.styling import apply_theme, format_plotly_figure

st.set_page_config(page_title="High-Demand Analysis | Mobility Ops", layout="wide")
apply_theme()

st.title("High-Demand Methodology & Statistical Analysis")
st.caption(
    "City-specific 85th percentile dynamic demand segmentation and behavioral correlation matrices."
)

# 1. Methodology Briefing
st.markdown(
    """
    <div class="briefing-card">
        <div style="font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; margin-bottom: 6px;">
            Operational Methodology Note
        </div>
        <div class="briefing-body">
            Rather than applying a naive static request threshold across all markets, the engine computes a 
            <strong>city-specific dynamic 85th percentile volume threshold</strong>:
            <code>P85(Hourly Volume)</code>. Hours where dispatch request volume exceeds this threshold are classified as <strong>High-Demand Strain Regimes</strong>.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 2. Correlation Matrices
corr_data, c_lat = fetch_correlation_data()

if corr_data:
    st.subheader("Behavioral Correlation Matrices")
    st.caption(
        "Quantifying the relationship between driver supply acceptance, surge multipliers, and rider cancellation."
    )

    c_mat1, c_mat2 = st.columns(2)

    with c_mat1:
        st.markdown("#### Pearson Linear Correlation")
        fig_pearson = px.imshow(
            corr_data["pearson"],
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1.0,
            zmax=1.0,
        )
        format_plotly_figure(fig_pearson, height=320, title="Pearson Correlation Matrix")
        st.plotly_chart(fig_pearson, width="stretch")

    with c_mat2:
        st.markdown("#### Spearman Rank Correlation (Monotonic)")
        fig_spearman = px.imshow(
            corr_data["spearman"],
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            zmin=-1.0,
            zmax=1.0,
        )
        format_plotly_figure(fig_spearman, height=320, title="Spearman Rank Correlation Matrix")
        st.plotly_chart(fig_spearman, width="stretch")

    r_val = corr_data.get("acceptance_vs_cancellation_r", -0.85)
    p_val = corr_data.get("acceptance_vs_cancellation_p", 0.0)
    p_str = "< 0.0001" if p_val < 0.0001 else f"{p_val:.4f}"

    st.markdown(
        f"""
        <div class="briefing-card" style="margin-top: 14px; font-size: 0.85rem;">
            <strong>Statistical Finding:</strong>
            Driver Acceptance Rate exhibits a strong inverse correlation with Rider Cancellation Rate
            (<code>r = {r_val:.2f}</code>, <code>p {p_str}</code>, N = {corr_data.get("sample_size", 0):,} hourly periods).
            Severe drops in driver acceptance during peak periods directly precede cascading rider cancellations.
        </div>
        """,
        unsafe_allow_html=True,
    )

# 3. Cross-Metro Scatter Relationships
st.markdown("---")
st.subheader("Cross-Metro Behavioral Relationships")

city_summary_df, _ = fetch_city_summary()
city_list = city_summary_df["city"].tolist() if not city_summary_df.empty else ["Mumbai"]
selected_city = st.selectbox("Filter Metro:", options=["All Metros"] + city_list, index=0)

if selected_city == "All Metros":
    from src.database.executor import QueryExecutor

    q = QueryExecutor()
    plot_df = q.query_df(
        "SELECT city, acceptance_rate_pct, cancellation_rate_pct, avg_surge, total_requests, is_high_demand FROM fct_hourly_city_metrics;"
    )
else:
    plot_df, _ = fetch_city_trends(selected_city)

fig_rel = px.scatter(
    plot_df,
    x="acceptance_rate_pct",
    y="cancellation_rate_pct",
    color="avg_surge",
    size="total_requests",
    facet_col="is_high_demand" if selected_city == "All Metros" else None,
    color_continuous_scale="Viridis",
    labels={
        "acceptance_rate_pct": "Driver Acceptance (%)",
        "cancellation_rate_pct": "Rider Cancellation (%)",
        "avg_surge": "Surge Multiplier",
        "total_requests": "Hourly Volume",
    },
)
format_plotly_figure(fig_rel, height=400, title="Cross-Regime Acceptance vs. Cancellation")
st.plotly_chart(fig_rel, width="stretch")
