"""Unit tests for deterministic operational diagnosis generation."""

from src.analytics.diagnosis import diagnosis_engine


def test_diagnosis_critical_city():
    city_data = {
        "city": "Mumbai",
        "cancellation_delta_pp": 16.0,
        "acceptance_delta_pp": -34.0,
        "surge_delta": 1.30,
        "normal_cancellation_pct": 7.0,
        "high_demand_cancellation_pct": 23.0,
        "normal_acceptance_pct": 88.0,
        "high_demand_acceptance_pct": 54.0,
        "normal_avg_surge": 1.05,
        "high_demand_avg_surge": 2.35,
        "degraded_hd_periods": 10,
        "total_hd_periods": 10,
        "consistency_pct": 100.0,
        "operational_risk_status": "CRITICAL",
    }
    diag = diagnosis_engine.generate_city_diagnosis(city_data)
    assert diag["risk_status"] == "CRITICAL"
    assert "Mumbai" in diag["narrative"]
    assert "16.0 percentage points" in diag["narrative"]
    assert "100.0% consistency" in diag["narrative"]
    assert diag["dominant_change"] == "Driver Acceptance Drop"


def test_diagnosis_healthy_city():
    city_data = {
        "city": "Singapore",
        "cancellation_delta_pp": 3.0,
        "acceptance_delta_pp": -8.0,
        "surge_delta": 0.40,
        "normal_cancellation_pct": 4.0,
        "high_demand_cancellation_pct": 7.0,
        "normal_acceptance_pct": 94.0,
        "high_demand_acceptance_pct": 86.0,
        "normal_avg_surge": 1.05,
        "high_demand_avg_surge": 1.45,
        "degraded_hd_periods": 2,
        "total_hd_periods": 10,
        "consistency_pct": 20.0,
        "operational_risk_status": "HEALTHY",
    }
    diag = diagnosis_engine.generate_city_diagnosis(city_data)
    assert diag["risk_status"] == "HEALTHY"
    assert "RESILIENT" in diag["narrative"]
