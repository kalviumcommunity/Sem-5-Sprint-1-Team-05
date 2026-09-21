"""Deterministic Synthetic Ride-Sharing Data Generator.

Simulates realistic operational event logs across multiple metro markets with
varying supply-demand elasticities, rush hours, surge dynamics, and driver/rider behaviors.
"""

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from src.utils.logger import logger

CITY_PROFILES = {
    "Mumbai": {
        "base_hourly_demand": 450,
        "rush_multiplier": 3.2,
        "normal_acceptance": 0.88,
        "high_demand_acceptance": 0.54,  # Severe unacceptance
        "normal_cancellation": 0.07,
        "high_demand_cancellation": 0.23,  # Severe cancellation
        "normal_surge": 1.05,
        "high_demand_surge": 2.35,
        "avg_base_fare": 180.0,
    },
    "Delhi": {
        "base_hourly_demand": 500,
        "rush_multiplier": 3.0,
        "normal_acceptance": 0.84,
        "high_demand_acceptance": 0.58,  # Severe unacceptance
        "normal_cancellation": 0.08,
        "high_demand_cancellation": 0.21,  # High cancellation
        "normal_surge": 1.08,
        "high_demand_surge": 2.20,
        "avg_base_fare": 200.0,
    },
    "Bengaluru": {
        "base_hourly_demand": 380,
        "rush_multiplier": 2.8,
        "normal_acceptance": 0.82,
        "high_demand_acceptance": 0.65,  # Moderate deterioration
        "normal_cancellation": 0.09,
        "high_demand_cancellation": 0.16,
        "normal_surge": 1.10,
        "high_demand_surge": 1.85,
        "avg_base_fare": 160.0,
    },
    "Hyderabad": {
        "base_hourly_demand": 300,
        "rush_multiplier": 2.2,
        "normal_acceptance": 0.89,
        "high_demand_acceptance": 0.74,  # Mild deterioration
        "normal_cancellation": 0.06,
        "high_demand_cancellation": 0.12,
        "normal_surge": 1.04,
        "high_demand_surge": 1.55,
        "avg_base_fare": 140.0,
    },
    "Chennai": {
        "base_hourly_demand": 260,
        "rush_multiplier": 2.0,
        "normal_acceptance": 0.90,
        "high_demand_acceptance": 0.78,
        "normal_cancellation": 0.05,
        "high_demand_cancellation": 0.10,
        "normal_surge": 1.02,
        "high_demand_surge": 1.40,
        "avg_base_fare": 130.0,
    },
    "Singapore": {
        "base_hourly_demand": 420,
        "rush_multiplier": 2.4,
        "normal_acceptance": 0.94,
        "high_demand_acceptance": 0.86,  # Highly resilient market
        "normal_cancellation": 0.04,
        "high_demand_cancellation": 0.07,
        "normal_surge": 1.05,
        "high_demand_surge": 1.45,
        "avg_base_fare": 320.0,
    },
    "London": {
        "base_hourly_demand": 480,
        "rush_multiplier": 2.6,
        "normal_acceptance": 0.86,
        "high_demand_acceptance": 0.71,
        "normal_cancellation": 0.07,
        "high_demand_cancellation": 0.15,
        "normal_surge": 1.10,
        "high_demand_surge": 1.90,
        "avg_base_fare": 450.0,
    },
    "New York": {
        "base_hourly_demand": 550,
        "rush_multiplier": 2.9,
        "normal_acceptance": 0.83,
        "high_demand_acceptance": 0.68,
        "normal_cancellation": 0.08,
        "high_demand_cancellation": 0.17,
        "normal_surge": 1.12,
        "high_demand_surge": 2.05,
        "avg_base_fare": 520.0,
    },
}


def generate_operational_dataset(
    start_date: datetime = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc),
    days: int = 14,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Generates deterministic synthetic ride-sharing event log DataFrame."""
    np.random.seed(random_seed)
    records = []
    request_number = 0

    logger.info(
        f"Generating operational dataset for {len(CITY_PROFILES)} cities over {days} days..."
    )

    # RUSH HOUR WINDOWS: Morning rush (8-10 AM) & Evening rush (18-21 PM)
    morning_rush = {8, 9, 10}
    evening_rush = {18, 19, 20, 21}

    for day_offset in range(days):
        current_day = start_date + timedelta(days=day_offset)
        is_weekend = current_day.weekday() in [5, 6]

        for hour in range(24):
            current_hour_dt = current_day.replace(hour=hour)
            is_rush = (hour in morning_rush or hour in evening_rush) and not is_weekend
            # Weekend nightlife rush (22 PM - 1 AM)
            if is_weekend and (hour in {21, 22, 23, 0, 1}):
                is_rush = True

            for city, profile in CITY_PROFILES.items():
                # Determine demand volume
                demand_factor = profile["rush_multiplier"] if is_rush else 1.0
                # Add natural Poisson/Gaussian noise
                noise = np.random.normal(1.0, 0.08)
                n_requests = max(
                    10, int(profile["base_hourly_demand"] * demand_factor * noise / 4)
                )  # Scale to realistic per-hour batch

                # Probability parameters for this hour
                if is_rush:
                    p_accept = profile["high_demand_acceptance"]
                    p_cancel = profile["high_demand_cancellation"]
                    surge_mean = profile["high_demand_surge"]
                    surge_std = 0.25
                else:
                    p_accept = profile["normal_acceptance"]
                    p_cancel = profile["normal_cancellation"]
                    surge_mean = profile["normal_surge"]
                    surge_std = 0.05

                # Generate batch vectors for performance
                accept_vec = np.random.binomial(1, p_accept, n_requests)
                cancel_vec = np.random.binomial(1, p_cancel, n_requests)
                surge_vec = np.clip(
                    np.random.normal(surge_mean, surge_std, n_requests), 1.0, 4.5
                ).round(2)
                base_fare_vec = np.clip(
                    np.random.normal(
                        profile["avg_base_fare"], profile["avg_base_fare"] * 0.2, n_requests
                    ),
                    50.0,
                    2000.0,
                ).round(2)

                # Estimated arrival ETA (longer when unacceptance is high)
                base_eta = 4.0 if not is_rush else 9.0
                eta_vec = np.clip(np.random.exponential(base_eta, n_requests), 1.0, 35.0).round(1)

                # Minute-level distribution within the hour
                minutes = np.random.randint(0, 60, n_requests)
                seconds = np.random.randint(0, 60, n_requests)

                for i in range(n_requests):
                    req_ts = current_hour_dt + timedelta(
                        minutes=int(minutes[i]), seconds=int(seconds[i])
                    )
                    driver_acc = int(accept_vec[i])
                    rider_canc = int(cancel_vec[i])

                    # Completed if accepted and not cancelled
                    trip_comp = 1 if (driver_acc == 1 and rider_canc == 0) else 0

                    # Cancellation taxonomy
                    cancellation_reason = None
                    if rider_canc == 1:
                        reasons = ["driver_delayed", "high_eta", "fare_shock", "changed_mind"]
                        weights = [0.45, 0.35, 0.15, 0.05] if is_rush else [0.25, 0.25, 0.10, 0.40]
                        cancellation_reason = np.random.choice(reasons, p=weights)

                    records.append(
                        {
                            "request_id": f"REQ-{request_number:012d}",
                            "city": city,
                            "timestamp": req_ts.strftime("%Y-%m-%d %H:%M:%S"),
                            "driver_id": f"DRV-{np.random.randint(1000, 9999)}",
                            "driver_accepted": driver_acc,
                            "rider_cancelled": rider_canc,
                            "cancellation_reason": cancellation_reason,
                            "surge_multiplier": float(surge_vec[i]),
                            "base_fare": float(base_fare_vec[i]),
                            "estimated_eta_min": float(eta_vec[i]),
                            "actual_wait_time_min": float(
                                round(eta_vec[i] * np.random.uniform(0.8, 1.4), 1)
                            ),
                            "trip_completed": trip_comp,
                            "trip_distance_km": float(round(np.random.uniform(2.0, 28.0), 2)),
                        }
                    )
                    request_number += 1

    df = pd.DataFrame(records)
    logger.info(f"Dataset generated successfully with {len(df):,} records.")
    return df
