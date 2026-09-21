-- Staging schema DDL for raw ride events
CREATE TABLE IF NOT EXISTS stg_ride_events (
    request_id VARCHAR PRIMARY KEY,
    city VARCHAR NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    date_hour_bucket TIMESTAMP NOT NULL,
    hour_of_day INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR NOT NULL,
    is_weekend INTEGER NOT NULL,
    driver_id VARCHAR,
    driver_accepted INTEGER NOT NULL,
    rider_cancelled INTEGER NOT NULL,
    cancellation_reason VARCHAR,
    surge_multiplier DOUBLE NOT NULL,
    base_fare DOUBLE NOT NULL,
    estimated_eta_min DOUBLE,
    actual_wait_time_min DOUBLE,
    trip_completed INTEGER NOT NULL,
    trip_distance_km DOUBLE
);

CREATE INDEX IF NOT EXISTS idx_stg_city_ts ON stg_ride_events(city, timestamp);
CREATE INDEX IF NOT EXISTS idx_stg_hour_bucket ON stg_ride_events(city, date_hour_bucket);
