"""Application settings and configuration parameters."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Project metadata
    PROJECT_NAME: str = "Ride-Sharing Operational Intelligence Platform"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    SAMPLE_DATA_DIR: Path = DATA_DIR / "sample"
    SQL_DIR: Path = BASE_DIR / "sql"

    # Database
    DUCKDB_PATH: Path = BASE_DIR / "data" / "processed" / "analytics.duckdb"

    # High Demand Methodology
    # We use P85 of city hourly demand volume as the standard high-demand period threshold
    HIGH_DEMAND_PERCENTILE: float = 85.0
    MIN_PERIODS_FOR_CONSISTENCY: int = 5

    # Statistical Anomaly Detection Thresholds
    CANCELLATION_ANOMALY_Z_SCORE: float = 2.0
    SURGE_ANOMALY_THRESHOLD: float = 2.0

    # Risk Category Thresholds (percentage points delta from baseline)
    CRITICAL_CANCELLATION_DELTA_PP: float = 10.0  # +10 pp or worse
    CRITICAL_ACCEPTANCE_DROP_PP: float = 15.0  # -15 pp or worse
    HIGH_CONSISTENCY_THRESHOLD: float = 0.60  # 60%+ of high-demand periods degraded

    # Application Port
    STREAMLIT_SERVER_PORT: int = 8501
    STREAMLIT_SERVER_HEADLESS: bool = True

    def ensure_directories(self) -> None:
        """Ensure all required filesystem directories exist."""
        for dir_path in [
            self.DATA_DIR,
            self.RAW_DATA_DIR,
            self.PROCESSED_DATA_DIR,
            self.SAMPLE_DATA_DIR,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
