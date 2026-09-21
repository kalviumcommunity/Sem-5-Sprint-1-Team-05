# Documented Assumptions — Ride-Sharing Intelligence Platform

## 1. High-Demand Period Identification
- **Assumption:** Demand elasticity and surge response operate primarily on a localized **1-hour temporal grain**.
- **Threshold Selection:** High-demand periods are defined on a per-city basis using the **85th percentile ($P_{85}$)** of hourly request volume within that metro.
- **Defensibility:** A flat global volume threshold would introduce bias, falsely classifying small but strained metros as normal and mega-cities as perpetually high-demand. The city-specific $P_{85}$ captures top-quartile strain while ensuring sufficient sample size for statistical consistency analysis.

## 2. Rider Experience Quantification
- **Assumption:** Rider friction is directly reflected in operational breakdown indicators:
  1. Rider cancellation frequency ($\text{RCR}$).
  2. Driver dispatch rejection / timeout ($(1 - \text{DAR})$).
  3. Surge pricing shock ($\text{Surge Multiplier} > 1.5\text{x}$).
- **Non-Invention Principle:** No artificial subjective satisfaction scores (e.g. 1-5 star ratings) are fabricated. All metrics represent observed behavioral actions.

## 3. Operational Consistency Definition
- **Assumption:** A city is only flagged for systemic operational risk if degraded outcomes recur across multiple high-demand windows.
- **Rule:** A high-demand period is considered degraded if its hourly cancellation rate exceeds the city's normal baseline by $\ge 4.0\text{ percentage points}$.
- **Consistency Score:** $C = \frac{N_{\text{degraded}}}{N_{\text{total HD}}}$. Metros with $C \ge 50\%$ and $\Delta_{\text{RCR}} \ge +8\text{ pp}$ or $\Delta_{\text{DAR}} \le -15\text{ pp}$ are classified as `CRITICAL`.
