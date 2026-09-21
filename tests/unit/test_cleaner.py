"""Unit tests for DataCleaner."""

import pandas as pd

from src.transformation.cleaner import DataCleaner


def test_cleaner_deduplication():
    df = pd.DataFrame(
        [
            {
                "request_id": "REQ-1",
                "city": "mumbai",
                "timestamp": "2026-08-01 10:00:00",
                "driver_accepted": 1,
                "rider_cancelled": 0,
                "surge_multiplier": 1.2,
                "base_fare": 100.0,
                "trip_completed": 1,
            },
            {
                "request_id": "REQ-1",
                "city": "mumbai",
                "timestamp": "2026-08-01 10:00:00",
                "driver_accepted": 1,
                "rider_cancelled": 0,
                "surge_multiplier": 1.2,
                "base_fare": 100.0,
                "trip_completed": 1,
            },
        ]
    )
    clean_df = DataCleaner.clean(df)
    assert len(clean_df) == 1
    assert clean_df.iloc[0]["city"] == "Mumbai"


def test_cleaner_temporal_extraction():
    df = pd.DataFrame(
        [
            {
                "request_id": "REQ-10",
                "city": "Delhi",
                "timestamp": "2026-08-01 08:30:00",
                "driver_accepted": 1,
                "rider_cancelled": 0,
                "surge_multiplier": 1.5,
                "base_fare": 150.0,
                "trip_completed": 1,
            }
        ]
    )
    clean_df = DataCleaner.clean(df)
    assert "date_hour_bucket" in clean_df.columns
    assert clean_df.iloc[0]["hour_of_day"] == 8


def test_cleaner_state_consistency():
    # If trip_completed is 1, rider_cancelled must be coerced to 0
    df = pd.DataFrame(
        [
            {
                "request_id": "REQ-20",
                "city": "Bengaluru",
                "timestamp": "2026-08-01 09:00:00",
                "driver_accepted": 1,
                "rider_cancelled": 1,
                "surge_multiplier": 1.0,
                "base_fare": 200.0,
                "trip_completed": 1,
            }
        ]
    )
    clean_df = DataCleaner.clean(df)
    assert clean_df.iloc[0]["rider_cancelled"] == 0
    assert clean_df.iloc[0]["trip_completed"] == 1
