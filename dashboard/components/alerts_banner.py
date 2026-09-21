"""Explainable Operational Alerts Component — Warm Editorial Palette."""
import pandas as pd
import streamlit as st


def render_operational_alerts(alerts_df: pd.DataFrame) -> None:
    """Renders structured operational alert cards in warm editorial style."""
    if alerts_df.empty:
        st.markdown(
            """
            <div style="background-color: rgba(93, 107, 46, 0.08); border: 1px solid rgba(93, 107, 46, 0.22);
                        border-radius: 6px; padding: 14px 18px; color: #5D6B2E; font-size: 0.85rem;">
                All operating metropolitan markets are within normal baseline limits.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown("### Operational Risk Alerts")

    cards_html = ""
    for _, row in alerts_df.iterrows():
        city        = row["city"]
        severity    = row["severity"]
        canc_delta  = row["cancellation_delta_pp"]
        acc_delta   = row["acceptance_delta_pp"]
        norm_canc   = row["normal_cancellation_pct"]
        hd_canc     = row["high_demand_cancellation_pct"]
        norm_acc    = row["normal_acceptance_pct"]
        hd_acc      = row["high_demand_acceptance_pct"]
        hd_surge    = row["high_demand_avg_surge"]
        degraded    = int(row["degraded_hd_periods"])
        total       = int(row["total_hd_periods"])
        consistency = row["consistency_pct"]

        pill_class     = "status-critical" if severity == "CRITICAL" else ("status-watch" if severity == "WATCH" else "status-healthy")
        border_accent  = "#B8471E" if severity == "CRITICAL" else "#B87418"
        value_color    = "#B8471E" if severity == "CRITICAL" else "#B87418"

        cards_html += f"""
        <div style="background-color: #F9F6EF; border: 1px solid #D4C9B0;
                    border-left: 3px solid {border_accent}; border-radius: 6px;
                    padding: 14px 18px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 0.95rem; font-weight: 700; color: #1C1917;">{city}</span>
                <span class="status-pill {pill_class}">
                    <span class="status-dot"></span>
                    {severity}
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
                        gap: 12px; font-size: 0.8rem; color: #524B42;">
                <div>
                    <span style="color: #8A7E72; font-size: 0.7rem; text-transform: uppercase;
                                 font-weight: 600; letter-spacing: 0.05em;">Rider Cancellation</span><br>
                    <span style="color: {value_color}; font-weight: 700;">{hd_canc:.1f}%</span>
                    <span style="color: #8A7E72;">vs {norm_canc:.1f}% baseline ({canc_delta:+.1f} pp)</span>
                </div>
                <div>
                    <span style="color: #8A7E72; font-size: 0.7rem; text-transform: uppercase;
                                 font-weight: 600; letter-spacing: 0.05em;">Driver Acceptance</span><br>
                    <span style="color: {value_color}; font-weight: 700;">{hd_acc:.1f}%</span>
                    <span style="color: #8A7E72;">vs {norm_acc:.1f}% baseline ({acc_delta:+.1f} pp)</span>
                </div>
                <div>
                    <span style="color: #8A7E72; font-size: 0.7rem; text-transform: uppercase;
                                 font-weight: 600; letter-spacing: 0.05em;">Surge Multiplier</span><br>
                    <span style="color: #1C1917; font-weight: 700;">{hd_surge:.2f}x</span>
                    <span style="color: #8A7E72;">(peak avg)</span>
                </div>
                <div>
                    <span style="color: #8A7E72; font-size: 0.7rem; text-transform: uppercase;
                                 font-weight: 600; letter-spacing: 0.05em;">Consistency</span><br>
                    <span style="color: #1C1917; font-weight: 700;">{degraded}/{total} windows</span>
                    <span style="color: #8A7E72;">({consistency:.1f}%)</span>
                </div>
            </div>
        </div>
        """

    st.markdown(cards_html, unsafe_allow_html=True)
