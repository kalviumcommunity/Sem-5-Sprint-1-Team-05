"""Enterprise Editorial Design System — Warm Beige & Olive Green Palette.

Inspired by Financial Times, The Economist, and Linear's light mode.
Warm off-white canvas, olive green accents, terracotta status indicators.
High contrast, readable, and professional without being flashy.
"""

CUSTOM_CSS = """
<style>
/* Enterprise Font Stack */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg-canvas:    #F7F4EF;
    --bg-panel:     #FBF9F6;
    --bg-card:      #F3EDE0;
    --border:       #D8CDBA;
    --border-strong:#C0B29A;
    --text-primary: #1F1B18;
    --text-secondary: #5B534A;
    --text-muted:   #8B8072;
    --accent:       #A28F6C; /* warm neutral beige accent */
    --olive:        #6B7850; /* subtle olive hint */
    --olive-light:  #99A073;
    --olive-faint:  rgba(107, 120, 80, 0.08);
    --terracotta:   #B8471E;
    --terra-faint:  rgba(184, 71, 30, 0.06);
    --amber:        #B87418;
    --amber-faint:  rgba(184, 116, 24, 0.06);
    --sky:          #4A6B85;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    letter-spacing: -0.012em;
    color: #1C1917;
    background-color: #F5F0E8 !important;
}

/* Override Streamlit canvas background */
.stApp {
    background-color: #F5F0E8 !important;
}

.block-container {
    background-color: #F5F0E8 !important;
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 1280px !important;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    background-color: #EDE8DC !important;
    color: #1C1917 !important;
}

/* Top Application Header Strip */
.app-header-strip {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    background-color: #F9F6EF;
    border: 1px solid #D4C9B0;
    border-radius: 6px;
    margin-bottom: 24px;
}

.app-brand-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #1C1917;
    letter-spacing: -0.01em;
}

.app-brand-badge {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background-color: rgba(162, 143, 108, 0.12);
    color: var(--text-primary);
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(192, 178, 154, 0.22);
}

/* Status Badges */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
}

.status-critical {
    background-color: rgba(184, 71, 30, 0.08);
    color: #B8471E;
    border: 1px solid rgba(184, 71, 30, 0.22);
}

.status-watch {
    background-color: rgba(184, 116, 24, 0.07);
    color: #B87418;
    border: 1px solid rgba(184, 116, 24, 0.18);
}

.status-healthy {
    background-color: rgba(162, 143, 108, 0.10);
    color: var(--olive);
    border: 1px solid rgba(162, 143, 108, 0.18);
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
}

.status-critical .status-dot { background-color: #B8471E; }
.status-watch    .status-dot { background-color: #B87418; }
.status-healthy  .status-dot { background-color: var(--olive); }

/* Delta color helpers */
.delta-bad     { color: #B8471E; font-weight: 600; }
.delta-good    { color: var(--olive); font-weight: 600; }
.delta-neutral { color: var(--sky); font-weight: 600; }

/* Diagnosis Briefing Card */
.briefing-card {
    background-color: var(--bg-panel);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 18px 22px;
    margin-bottom: 20px;
}

.briefing-body {
    font-size: 0.92rem;
    line-height: 1.65;
    color: #3B3530;
    margin-bottom: 14px;
}

.briefing-action {
    font-size: 0.84rem;
    color: var(--olive);
    background: rgba(162, 143, 108, 0.06);
    border: 1px solid rgba(192, 178, 154, 0.12);
    padding: 10px 14px;
    border-radius: 4px;
}

/* Section Headers */
h1 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.25rem !important;
}

h2 {
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    color: #1C1917 !important;
    letter-spacing: -0.015em !important;
}

h3 {
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: #2A2522 !important;
    letter-spacing: -0.01em !important;
}

/* Caption / muted text */
.stCaption p {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #1C1917 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: #8A7E72 !important;
}

/* Buttons */
div.stButton > button {
    background-color: #EDE8DC !important;
    color: #1C1917 !important;
    border: 1px solid #B5A98A !important;
    border-radius: 5px !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 6px 14px !important;
    transition: all 0.15s ease !important;
}

div.stButton > button:hover {
    background-color: #DDD6C8 !important;
    border-color: #8A7E72 !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
    background-color: #F9F6EF !important;
    border-color: #D4C9B0 !important;
    color: #1C1917 !important;
}

/* Streamlit metric override */
div[data-testid="stMetric"] {
    background-color: var(--bg-panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 12px 16px;
}

div[data-testid="stMetricValue"] {
    color: #1C1917 !important;
}

div[data-testid="stMetricLabel"] {
    color: #8A7E72 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}

/* Info/warning boxes */
div[data-testid="stInfo"] {
    background-color: rgba(162, 143, 108, 0.08) !important;
    border: 1px solid rgba(192, 178, 154, 0.12) !important;
    color: #4A4A3F !important;
    border-radius: 6px !important;
}

/* Dataframe */
div[data-testid="stDataFrame"] {
    border: 1px solid #D4C9B0 !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* Horizontal rule */
hr {
    border-color: #D4C9B0 !important;
    margin: 20px 0 !important;
}

/* Expander */
details summary {
    color: #524B42 !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
}

</style>
"""


def apply_theme():
    """Injects custom CSS theme."""
    import streamlit as st

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Plotly chart configuration for warm editorial palette
PLOTLY_COLORS = {
    "primary":    "#5D6B2E",   # olive green
    "secondary":  "#B87418",   # warm amber
    "danger":     "#B8471E",   # terracotta
    "info":       "#2E6B8A",   # muted sky
    "muted":      "#8A7E72",   # warm gray
}

CHART_COLOR_SEQUENCE = [
    "#A28F6C",  # warm beige accent
    "#6B7850",  # subtle olive
    "#B87418",  # amber
    "#B8471E",  # terracotta
    "#4A6B85",  # slate/sky
    "#8B8072",  # muted
    "#7A5C3D",  # warm brown
    "#4A5C8A",  # slate blue
]


def format_plotly_figure(fig, height: int = 400, title: str | None = None):
    """Applies clean editorial warm-light styling to Plotly charts."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        title={
            "text": title or "",
            "font": {"size": 13, "color": "#1C1917", "family": "Inter"},
            "x": 0.0,
            "xanchor": "left",
        }
        if title
        else None,
        margin={"l": 10, "r": 10, "t": 40 if title else 16, "b": 20},
        plot_bgcolor="#FBF9F6",
        paper_bgcolor="#FBF9F6",
        font={"family": "Inter", "color": "#5B534A", "size": 11},
        xaxis={
            "gridcolor": "rgba(216, 205, 186, 0.28)",
            "zerolinecolor": "rgba(216, 205, 186, 0.45)",
            "showline": True,
            "linecolor": "#D8CDBA",
            "tickfont": {"size": 10, "color": "#8B8072"},
        },
        yaxis={
            "gridcolor": "rgba(216, 205, 186, 0.28)",
            "zerolinecolor": "rgba(216, 205, 186, 0.45)",
            "showline": True,
            "linecolor": "#D8CDBA",
            "tickfont": {"size": 10, "color": "#8B8072"},
        },
        legend={
            "font": {"size": 10, "color": "#524B42"},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)",
        },
        hoverlabel={
            "bgcolor": "#F9F6EF",
            "font_size": 11,
            "font_family": "Inter",
            "font_color": "#1C1917",
            "bordercolor": "#D4C9B0",
        },
        colorway=CHART_COLOR_SEQUENCE,
    )
    return fig
