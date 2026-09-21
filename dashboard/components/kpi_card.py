"""Enterprise Metric & KPI Card Component — Warm Editorial Palette."""
import streamlit as st

# Warm editorial palette tokens
_CARD_BG      = "#F9F6EF"
_CARD_BORDER  = "#D4C9B0"
_LABEL_COLOR  = "#8A7E72"
_VALUE_COLOR  = "#1C1917"

_DELTA_COLORS = {
    "delta-bad":     "#B8471E",  # terracotta
    "delta-good":    "#5D6B2E",  # olive
    "delta-neutral": "#2E6B8A",  # sky blue
    "":              "#8A7E72",  # muted
}


def render_stat_strip(stats_list: list[dict]) -> None:
    """Renders a horizontal stat strip using native Streamlit columns.

    Each dict in stats_list should contain:
    - title: str
    - value: str
    - sub_text: str | None
    - delta_class: 'delta-bad' | 'delta-good' | 'delta-neutral' | ''
    """
    cols = st.columns(len(stats_list))

    for col, item in zip(cols, stats_list):
        title       = item.get("title", "")
        value       = item.get("value", "")
        sub_text    = item.get("sub_text", "")
        delta_class = item.get("delta_class", "")
        color       = _DELTA_COLORS.get(delta_class, "#8A7E72")

        sub_html = (
            f'<span style="color:{color}; font-size:0.76rem; font-weight:500;">{sub_text}</span>'
            if sub_text
            else ""
        )

        with col:
            st.markdown(
                f"""
                <div style="
                    background-color: {_CARD_BG};
                    border: 1px solid {_CARD_BORDER};
                    border-radius: 6px;
                    padding: 14px 18px;
                    height: 100%;
                ">
                    <div style="
                        font-size: 0.7rem;
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: 0.06em;
                        color: {_LABEL_COLOR};
                        margin-bottom: 6px;
                    ">{title}</div>
                    <div style="
                        font-size: 1.5rem;
                        font-weight: 700;
                        color: {_VALUE_COLOR};
                        line-height: 1.2;
                        margin-bottom: 4px;
                        font-variant-numeric: tabular-nums;
                    ">{value}</div>
                    <div style="margin-top: 4px;">{sub_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div style='margin-bottom: 18px;'></div>", unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: str,
    delta: str | None = None,
    delta_type: str = "neutral",
    subtitle: str | None = None,
) -> None:
    """Renders a single clean enterprise metric panel."""
    delta_color = (
        "#B8471E" if delta_type == "positive"
        else ("#5D6B2E" if delta_type == "negative" else "#2E6B8A")
    )
    delta_html = (
        f'<div style="color:{delta_color}; font-size:0.78rem; font-weight:500; margin-top:4px;">{delta}</div>'
        if delta else ""
    )
    sub_html = (
        f'<div style="font-size:0.74rem; color:{_LABEL_COLOR}; margin-top:2px;">{subtitle}</div>'
        if subtitle else ""
    )

    st.markdown(
        f"""
        <div style="
            background-color: {_CARD_BG};
            border: 1px solid {_CARD_BORDER};
            border-radius: 6px;
            padding: 14px 18px;
            margin-bottom: 12px;
        ">
            <div style="
                font-size: 0.7rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: {_LABEL_COLOR};
                margin-bottom: 6px;
            ">{title}</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {_VALUE_COLOR};
                line-height: 1.2;
            ">{value}</div>
            {delta_html}
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
