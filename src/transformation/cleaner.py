"""Data Transformation and Cleaning Engine."""

import pandas as pd

from src.utils.logger import logger


class DataCleaner:
    """Transforms raw ride-sharing event telemetry into clean, analytical-ready format."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        """Executes full cleaning and normalization pipeline on ride events."""
        initial_count = len(df)
        logger.info(f"Starting data cleaning pipeline on {initial_count} records.")

        df = df.copy()

        # 1. Deduplicate by request_id if present
        if "request_id" in df.columns:
            df = df.drop_duplicates(subset=["request_id"], keep="last")
            dedup_count = initial_count - len(df)
            if dedup_count > 0:
                logger.info(f"Deduplicated {dedup_count} duplicate request_id records.")

        # 2. Text normalization on categorical fields
        if "city" in df.columns:
            df["city"] = df["city"].astype(str).str.strip().str.title()

        if "cancellation_reason" in df.columns:
            df["cancellation_reason"] = (
                df["cancellation_reason"]
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({"nan": None, "none": None, "": None})
            )

        # 3. Datetime parsing and temporal feature extraction
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            # Drop invalid timestamps
            df = df.dropna(subset=["timestamp"])

            # Extract temporal features (vectorized)
            df["date_hour_bucket"] = df["timestamp"].dt.floor("h")
            df["hour_of_day"] = df["timestamp"].dt.hour
            df["day_of_week"] = df["timestamp"].dt.dayofweek
            df["day_name"] = df["timestamp"].dt.day_name()
            df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

        # 4. Type casting and range enforcement
        if "driver_accepted" in df.columns:
            df["driver_accepted"] = (
                pd.to_numeric(df["driver_accepted"], errors="coerce").fillna(0).astype(int)
            )
            df["driver_accepted"] = df["driver_accepted"].clip(0, 1)

        if "rider_cancelled" in df.columns:
            df["rider_cancelled"] = (
                pd.to_numeric(df["rider_cancelled"], errors="coerce").fillna(0).astype(int)
            )
            df["rider_cancelled"] = df["rider_cancelled"].clip(0, 1)

        if "trip_completed" in df.columns:
            df["trip_completed"] = (
                pd.to_numeric(df["trip_completed"], errors="coerce").fillna(0).astype(int)
            )
            df["trip_completed"] = df["trip_completed"].clip(0, 1)

            # Enforce mutual exclusivity: if completed, cancellation must be 0
            completed_mask = df["trip_completed"] == 1
            df.loc[completed_mask, "rider_cancelled"] = 0

        if "surge_multiplier" in df.columns:
            df["surge_multiplier"] = pd.to_numeric(df["surge_multiplier"], errors="coerce").fillna(
                1.0
            )
            df["surge_multiplier"] = df["surge_multiplier"].clip(1.0, 10.0)

        if "base_fare" in df.columns:
            df["base_fare"] = pd.to_numeric(df["base_fare"], errors="coerce").fillna(0.0)

        logger.info(
            f"Cleaning completed. {len(df)} valid records retained ({round(len(df) / initial_count * 100, 1)}%)."
        )
        return df
