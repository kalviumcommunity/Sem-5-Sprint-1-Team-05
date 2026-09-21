"""DuckDB Connection Manager."""

import threading
from pathlib import Path
from typing import Optional

import duckdb

from src.config.settings import settings
from src.utils.logger import logger


class DatabaseManager:
    """Manages thread-safe DuckDB connection lifecycles and migrations."""

    _instance: Optional["DatabaseManager"] = None
    _lock = threading.Lock()

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.DUCKDB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: duckdb.DuckDBPyConnection | None = None

    @classmethod
    def get_instance(cls, db_path: Path | None = None) -> "DatabaseManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path)
            return cls._instance

    def get_connection(self, read_only: bool = True) -> duckdb.DuckDBPyConnection:
        """Returns active DuckDB connection. Defaults to read_only=True for safe concurrent queries."""
        if self._connection is None:
            logger.info(f"Establishing DuckDB connection to {self.db_path} (read_only={read_only})")
            try:
                self._connection = duckdb.connect(str(self.db_path), read_only=read_only)
            except duckdb.IOException as e:
                logger.warning(
                    f"File lock on {self.db_path} detected ({e}), initializing resilient in-memory reader..."
                )
                self._connection = duckdb.connect(":memory:")
                parquet_path = settings.PROCESSED_DATA_DIR / "ride_events_clean.parquet"
                if parquet_path.exists():
                    self._connection.execute(
                        f"CREATE TABLE stg_ride_events AS SELECT * FROM read_parquet('{parquet_path}');"
                    )
                    for mart_file in [
                        "fct_hourly_city_metrics.sql",
                        "mart_city_high_demand_summary.sql",
                        "mart_operational_anomalies.sql",
                    ]:
                        mart_path = settings.SQL_DIR / "marts" / mart_file
                        if mart_path.exists():
                            with open(mart_path) as f:
                                self._connection.execute(f.read())
        return self._connection

    def get_write_connection(self) -> duckdb.DuckDBPyConnection:
        """Closes existing read connection and returns dedicated write connection."""
        self.close()
        logger.info(f"Establishing DuckDB write connection to {self.db_path}")
        self._connection = duckdb.connect(str(self.db_path), read_only=False)
        return self._connection

    def close(self) -> None:
        """Safely closes DuckDB connection."""
        if self._connection is not None:
            try:
                self._connection.close()
            except duckdb.Error as e:
                logger.debug(f"DuckDB close notice: {e}")
            self._connection = None
            logger.info("DuckDB connection closed.")


db_manager = DatabaseManager.get_instance()
