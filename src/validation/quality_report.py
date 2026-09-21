"""Data Quality Auditor & Report Generator."""

from typing import Any

import pandas as pd

from src.validation.schema import REQUIRED_COLUMNS


class DataQualityReport:
    """Evaluates raw and processed datasets against data quality gates."""

    @staticmethod
    def inspect(df: pd.DataFrame) -> dict[str, Any]:
        """Performs comprehensive quality inspection of a DataFrame."""
        total_rows = len(df)
        if total_rows == 0:
            return {
                "status": "FAILED",
                "total_rows": 0,
                "errors": ["DataFrame is empty"],
                "passed_gates": False,
            }

        missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_required:
            return {
                "status": "FAILED",
                "total_rows": total_rows,
                "errors": [f"Missing required columns: {missing_required}"],
                "passed_gates": False,
            }

        # Null analysis
        null_counts = df.isnull().sum().to_dict()
        null_percentages = {
            col: round(float(count / total_rows * 100), 2) for col, count in null_counts.items()
        }

        # Duplicate analysis on primary key if present
        duplicate_ids = 0
        if "request_id" in df.columns:
            duplicate_ids = int(df["request_id"].duplicated().sum())

        # Range and domain boundary violations
        violations: list[str] = []
        if "surge_multiplier" in df.columns:
            invalid_surge = ((df["surge_multiplier"] < 1.0) | (df["surge_multiplier"] > 10.0)).sum()
            if invalid_surge > 0:
                violations.append(
                    f"{invalid_surge} records with surge_multiplier outside [1.0, 10.0]"
                )

        if "driver_accepted" in df.columns:
            invalid_acc = (~df["driver_accepted"].isin([0, 1])).sum()
            if invalid_acc > 0:
                violations.append(f"{invalid_acc} records with non-binary driver_accepted")

        if "rider_cancelled" in df.columns:
            invalid_canc = (~df["rider_cancelled"].isin([0, 1])).sum()
            if invalid_canc > 0:
                violations.append(f"{invalid_canc} records with non-binary rider_cancelled")

        # Inconsistency: trip_completed == 1 and rider_cancelled == 1
        inconsistent_trips = 0
        if "trip_completed" in df.columns and "rider_cancelled" in df.columns:
            inconsistent_trips = int(
                ((df["trip_completed"] == 1) & (df["rider_cancelled"] == 1)).sum()
            )
            if inconsistent_trips > 0:
                violations.append(
                    f"{inconsistent_trips} records marked both completed and cancelled"
                )

        passed_gates = len(violations) == 0 and duplicate_ids == 0

        # Calculate a quality score (0 - 100%)
        error_rows = duplicate_ids + inconsistent_trips
        quality_score = max(0.0, round(float((total_rows - error_rows) / total_rows * 100), 2))

        return {
            "status": "PASSED" if passed_gates else "WARNINGS_FOUND",
            "total_rows": total_rows,
            "duplicate_ids": duplicate_ids,
            "inconsistent_trips": inconsistent_trips,
            "null_counts": null_counts,
            "null_percentages": null_percentages,
            "violations": violations,
            "quality_score": quality_score,
            "passed_gates": passed_gates,
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        }
