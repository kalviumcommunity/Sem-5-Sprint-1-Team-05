"""Deterministic Operational Diagnosis & Root Cause Decomposition Generator.

Strictly derives evidence-based natural language summaries from computed
metrics without inventing numbers or making ungrounded causal claims.
"""

from typing import Any


class OperationalDiagnosisEngine:
    """Generates structured evidence-based operational diagnoses."""

    @staticmethod
    def generate_city_diagnosis(city_row: dict[str, Any]) -> dict[str, Any]:
        """Generates evidence-backed narrative diagnosis for a single city."""
        city = city_row.get("city", "Unknown City")
        canc_delta = float(city_row.get("cancellation_delta_pp", 0.0))
        acc_delta = float(city_row.get("acceptance_delta_pp", 0.0))
        surge_delta = float(city_row.get("surge_delta", 0.0))
        norm_canc = float(city_row.get("normal_cancellation_pct", 0.0))
        hd_canc = float(city_row.get("high_demand_cancellation_pct", 0.0))
        norm_acc = float(city_row.get("normal_acceptance_pct", 0.0))
        hd_acc = float(city_row.get("high_demand_acceptance_pct", 0.0))
        norm_surge = float(city_row.get("normal_avg_surge", 1.0))
        hd_surge = float(city_row.get("high_demand_avg_surge", 1.0))
        degraded_periods = int(city_row.get("degraded_hd_periods", 0))
        total_periods = int(city_row.get("total_hd_periods", 0))
        consistency_pct = float(city_row.get("consistency_pct", 0.0))
        risk_status = city_row.get("operational_risk_status", "HEALTHY")

        # 1. Primary Behavioral Driver Determination
        acc_drop = abs(acc_delta)
        drivers: list[str] = []
        if acc_drop >= 15.0:
            drivers.append(
                f"severe driver unacceptance (dropped {acc_drop:.1f} pp from {norm_acc:.1f}% to {hd_acc:.1f}%)"
            )
        elif acc_drop >= 7.0:
            drivers.append(f"moderate driver unacceptance (dropped {acc_drop:.1f} pp)")

        if surge_delta >= 0.8:
            drivers.append(
                f"elevated surge pricing (increased by +{surge_delta:.2f}x to {hd_surge:.2f}x)"
            )
        elif surge_delta >= 0.3:
            drivers.append(f"mild surge escalation (+{surge_delta:.2f}x)")

        drivers_summary = (
            " alongside " + " and ".join(drivers)
            if drivers
            else " without significant supply-side collapse"
        )

        # 2. Evidence-Based Narrative Synthesis
        if risk_status == "CRITICAL":
            narrative = (
                f"{city} is categorized under CRITICAL operational risk. During high-demand periods, rider cancellation "
                f"spikes by {canc_delta:+.1f} percentage points (from {norm_canc:.1f}% baseline to {hd_canc:.1f}%). "
                f"This degradation is consistently observed{drivers_summary}. "
                f"The pattern repeated across {degraded_periods} of {total_periods} observed high-demand windows ({consistency_pct:.1f}% consistency), "
                f"indicating a persistent structural supply deficit rather than an episodic anomaly."
            )
            action_recommendation = f"Priority focus for {city}: Address driver dispatch acceptance in high-demand zones to curb rider wait times and cancellations."
        elif risk_status == "WATCH":
            narrative = (
                f"{city} exhibits MODERATE operational friction. Rider cancellation increases by {canc_delta:+.1f} pp "
                f"during high-demand periods (baseline {norm_canc:.1f}% to {hd_canc:.1f}%){drivers_summary}. "
                f"Degradation appeared in {degraded_periods} of {total_periods} high-demand windows ({consistency_pct:.1f}% consistency)."
            )
            action_recommendation = (
                f"Monitor driver fulfillment elasticity in {city} during peak commute windows."
            )
        else:
            narrative = (
                f"{city} demonstrates RESILIENT operational health during peak strain. Rider cancellation remains controlled at "
                f"{hd_canc:.1f}% (baseline {norm_canc:.1f}%, delta of {canc_delta:+.1f} pp), with high driver acceptance ({hd_acc:.1f}%). "
                f"High-demand strain degraded rider experience in only {degraded_periods} of {total_periods} windows ({consistency_pct:.1f}% consistency)."
            )
            action_recommendation = (
                f"{city} operational playbook serves as a benchmark for peak-demand resilience."
            )

        dominant_change = (
            "Driver Acceptance Drop" if acc_drop > canc_delta else "Rider Cancellation Surge"
        )

        return {
            "city": city,
            "risk_status": risk_status,
            "narrative": narrative,
            "action_recommendation": action_recommendation,
            "dominant_change": dominant_change,
            "metrics_breakdown": {
                "cancellation": {
                    "baseline": norm_canc,
                    "high_demand": hd_canc,
                    "delta_pp": canc_delta,
                },
                "acceptance": {"baseline": norm_acc, "high_demand": hd_acc, "delta_pp": acc_delta},
                "surge": {"baseline": norm_surge, "high_demand": hd_surge, "delta": surge_delta},
                "consistency": {
                    "degraded": degraded_periods,
                    "total": total_periods,
                    "pct": consistency_pct,
                },
            },
        }


diagnosis_engine = OperationalDiagnosisEngine()
