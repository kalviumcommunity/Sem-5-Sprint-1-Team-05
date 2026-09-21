"""Unit tests for schema and quality report validation."""

from datetime import datetime, timezone

import pandas as pd

from src.validation.quality_report import DataQualityReport
from src.validation.schema import RideEventRecord


def test_schema_valid_record():
    record = RideEventRecord(
        request_id="REQ-TEST1",
        city="Mumbai",
        timestamp=datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
        driver_accepted=1,
        rider_cancelled=0,
        surge_multiplier=1.25,
        base_fare=180.0,
        trip_completed=1,
    )
    assert record.city == "Mumbai"
    assert record.surge_multiplier == 1.25


def test_quality_report_detects_missing_cols():
    df = pd.DataFrame([{"request_id": "REQ-1", "city": "Delhi"}])
    report = DataQualityReport.inspect(df)
    assert report["status"] == "FAILED"
    assert report["passed_gates"] is False


def test_quality_report_detects_duplicates():
    df = pd.DataFrame(
        [
            {
                "request_id": "REQ-1",
                "city": "Mumbai",
                "timestamp": "2026-08-01",
                "driver_accepted": 1,
                "rider_cancelled": 0,
                "surge_multiplier": 1.0,
                "base_fare": 100,
                "trip_completed": 1,
            },
            {
                "request_id": "REQ-1",
                "city": "Mumbai",
                "timestamp": "2026-08-01",
                "driver_accepted": 1,
                "rider_cancelled": 0,
                "surge_multiplier": 1.0,
                "base_fare": 100,
                "trip_completed": 1,
            },
        ]
    )
    report = DataQualityReport.inspect(df)
    assert report["duplicate_ids"] == 1
    assert report["passed_gates"] is False
