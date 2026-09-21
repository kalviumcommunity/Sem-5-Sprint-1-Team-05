"""Validation schemas and boundary check models."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RideEventRecord(BaseModel):
    """Schema definition for an individual ride request dispatch event."""

    request_id: str = Field(..., description="Unique event identifier")
    city: str = Field(..., min_length=2, max_length=50, description="City / Metro region")
    timestamp: datetime = Field(..., description="UTC Timestamp of the request")
    driver_id: str | None = Field(None, description="Dispatched driver identifier")
    driver_accepted: int = Field(
        ..., ge=0, le=1, description="1 if driver accepted ping, 0 otherwise"
    )
    rider_cancelled: int = Field(..., ge=0, le=1, description="1 if rider cancelled, 0 otherwise")
    cancellation_reason: str | None = Field(None, max_length=50, description="Taxonomy reason")
    surge_multiplier: float = Field(..., ge=1.0, le=10.0, description="Surge multiplier applied")
    base_fare: float = Field(..., ge=0.0, le=5000.0, description="Base trip fare")
    estimated_eta_min: float | None = Field(
        None, ge=0.0, le=120.0, description="Estimated arrival ETA"
    )
    actual_wait_time_min: float | None = Field(
        None, ge=0.0, le=120.0, description="Actual waiting time"
    )
    trip_completed: int = Field(
        ..., ge=0, le=1, description="1 if trip reached destination, 0 otherwise"
    )
    trip_distance_km: float | None = Field(
        None, ge=0.0, le=200.0, description="Trip distance in km"
    )

    @field_validator("city")
    @classmethod
    def normalize_city(cls, v: str) -> str:
        return v.strip().title()

    @field_validator("rider_cancelled")
    @classmethod
    def validate_cancellation_consistency(cls, v: int, info) -> int:
        data = info.data
        if "trip_completed" in data and data["trip_completed"] == 1 and v == 1:
            raise ValueError("Inconsistent state: trip cannot be both completed and cancelled.")
        return v


REQUIRED_COLUMNS = [
    "request_id",
    "city",
    "timestamp",
    "driver_accepted",
    "rider_cancelled",
    "surge_multiplier",
    "base_fare",
    "trip_completed",
]
