"""Data Ingestion & Orchestration Pipeline."""

from pathlib import Path
from typing import Any

import pandas as pd

from src.config.settings import settings
from src.database.connection import DatabaseManager, db_manager
from src.database.executor import QueryExecutor
from src.ingestion.data_generator import generate_operational_dataset
from src.transformation.cleaner import DataCleaner
from src.utils.logger import logger
from src.validation.quality_report import DataQualityReport


class IngestionPipeline:
    """Orchestrates extraction, validation, transformation, and DuckDB mart creation."""

    def __init__(
        self,
        raw_csv_path: Path | None = None,
        db_manager_instance: DatabaseManager | None = None,
    ):
        self.raw_csv_path = raw_csv_path or (settings.RAW_DATA_DIR / "ride_events_raw.csv")
        self.db_manager = db_manager_instance or db_manager
        self.executor = QueryExecutor()

    def run(self, force_regenerate: bool = False, days: int = 14) -> dict[str, Any]:
        """Executes end-to-end pipeline run."""
        logger.info("Initializing Ride-Sharing Operational Pipeline execution...")

        # Step 1: Ingestion / Extraction
        if not self.raw_csv_path.exists() or force_regenerate:
            logger.info(
                "Raw data file not found or regeneration requested. Generating synthetic operational data..."
            )
            raw_df = generate_operational_dataset(days=days)
            self.raw_csv_path.parent.mkdir(parents=True, exist_ok=True)
            raw_df.to_csv(self.raw_csv_path, index=False)
            logger.info(f"Raw dataset written to {self.raw_csv_path}")
        else:
            logger.info(f"Loading raw dataset from {self.raw_csv_path}...")
            raw_df = pd.read_csv(self.raw_csv_path)

        # Step 2: Quality Gate Inspection
        quality_report = DataQualityReport.inspect(raw_df)
        logger.info(
            f"Quality Gate Status: {quality_report['status']} (Score: {quality_report['quality_score']}%)"
        )

        # Step 3: Transformation & Cleaning
        clean_df = DataCleaner.clean(raw_df)

        # Save processed parquet backup
        processed_parquet_path = settings.PROCESSED_DATA_DIR / "ride_events_clean.parquet"
        clean_df.to_parquet(processed_parquet_path, index=False)

        # Step 4: Loading into DuckDB Staging
        conn = self.db_manager.get_write_connection()

        # Read and apply staging DDL
        staging_ddl_path = settings.SQL_DIR / "schema" / "staging.sql"
        with open(staging_ddl_path, "r") as f:
            staging_ddl = f.read()
        conn.execute(staging_ddl)

        # Register and insert dataframe into stg_ride_events with explicit column ordering
        conn.register("df_clean_view", clean_df)
        conn.execute("DELETE FROM stg_ride_events")
        conn.execute("""
            INSERT INTO stg_ride_events (
                request_id, city, timestamp, date_hour_bucket,
                hour_of_day, day_of_week, day_name, is_weekend,
                driver_id, driver_accepted, rider_cancelled, cancellation_reason,
                surge_multiplier, base_fare, estimated_eta_min, actual_wait_time_min,
                trip_completed, trip_distance_km
            )
            SELECT
                request_id, city, timestamp, date_hour_bucket,
                hour_of_day, day_of_week, day_name, is_weekend,
                driver_id, driver_accepted, rider_cancelled, cancellation_reason,
                surge_multiplier, base_fare, estimated_eta_min, actual_wait_time_min,
                trip_completed, trip_distance_km
            FROM df_clean_view
        """)
        conn.unregister("df_clean_view")
        logger.info(f"Loaded {len(clean_df):,} records into stg_ride_events table.")

        # Step 5: Execute SQL Data Marts
        mart_files = [
            settings.SQL_DIR / "marts" / "fct_hourly_city_metrics.sql",
            settings.SQL_DIR / "marts" / "mart_city_high_demand_summary.sql",
            settings.SQL_DIR / "marts" / "mart_operational_anomalies.sql",
        ]

        for sql_file in mart_files:
            logger.info(f"Executing SQL Mart script: {sql_file.name}...")
            with open(sql_file, "r") as f:
                sql_script = f.read()
            conn.execute(sql_script)

        # Release write lock
        self.db_manager.close()

        logger.info("Pipeline execution completed successfully.")
        return {
            "status": "SUCCESS",
            "raw_rows": len(raw_df),
            "clean_rows": len(clean_df),
            "quality_report": quality_report,
            "processed_parquet": str(processed_parquet_path),
        }


pipeline = IngestionPipeline()
