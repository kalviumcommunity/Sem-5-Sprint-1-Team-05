# Analytical Methodology — Ride-Sharing Operational Intelligence

## 1. Core Business Questions & Mathematical Answers

### Q1 — WHERE? (Geographic Risk Localization)
- **Methodology:** Cities are mapped onto the 4D Operational Risk Matrix (X: Driver Acceptance, Y: Rider Cancellation, Size: Demand Volume, Color: Surge/Risk).
- **Metric:** Cities located in the high-cancellation, low-acceptance quadrant (e.g. Mumbai, Delhi) are isolated and ranked by Delta Deterioration ($\Delta_{\text{RCR}}$).

### Q2 — WHAT? (Behavioral Variable Association)
- **Methodology:** Bivariate Pearson ($r$) and Spearman ($\rho$) correlation matrices evaluate relationships across all hourly operational records.
- **Finding:** Driver unacceptance exhibits a strong, statistically significant negative association with rider retention ($r = -0.85$, $p < 0.0001$). As drivers decline trips, rider wait times and cancellation rates rise monotonically.

### Q3 — WHEN? (Temporal Window Identification)
- **Methodology:** Fact rollups segment metrics by `hour_of_day`, `day_of_week`, and `is_weekend`. Peak friction clusters heavily during morning rush (8–10 AM) and evening rush (18–21 PM) on weekdays.

### Q4 — WHY? (Root Cause Decomposition — "What Changed?")
- **Methodology:** The system compares relative magnitudes of shift:
  $$\Delta_{\text{DAR}} = \text{DAR}_{\text{Normal}} - \text{DAR}_{\text{Peak}}$$
  $$\Delta_{\text{RCR}} = \text{RCR}_{\text{Peak}} - \text{RCR}_{\text{Normal}}$$
  $$\Delta_{\text{Surge}} = \text{Surge}_{\text{Peak}} - \text{Surge}_{\text{Normal}}$$
- **Finding:** In critical metros, driver acceptance drops by over 30 percentage points, demonstrating that driver supply withdrawal—rather than pure price sensitivity—is the dominant root cause.

### Q5 — HOW CONSISTENT? (Repeatability Quantification)
- **Methodology:** Consistency ratio $C = \frac{N_{\text{Degraded}}}{N_{\text{HD}}}$.
- **Result:** Mumbai and Delhi exhibit $\approx 100\%$ degradation consistency across all qualifying peak windows, confirming a persistent structural capacity gap.
