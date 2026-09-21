-- Fact Table: Pre-aggregated hourly metrics per city with dynamic high-demand classification
CREATE OR REPLACE TABLE fct_hourly_city_metrics AS
WITH hourly_raw AS (
    SELECT
        city,
        date_hour_bucket,
        hour_of_day,
        day_of_week,
        day_name,
        is_weekend,
        COUNT(request_id) AS total_requests,
        SUM(driver_accepted) AS accepted_requests,
        SUM(rider_cancelled) AS cancelled_requests,
        SUM(trip_completed) AS completed_trips,
        ROUND(AVG(driver_accepted) * 100.0, 2) AS acceptance_rate_pct,
        ROUND(AVG(rider_cancelled) * 100.0, 2) AS cancellation_rate_pct,
        ROUND(AVG(surge_multiplier), 3) AS avg_surge,
        ROUND(MEDIAN(surge_multiplier), 2) AS median_surge,
        ROUND(AVG(estimated_eta_min), 1) AS avg_estimated_eta,
        ROUND(AVG(actual_wait_time_min), 1) AS avg_actual_wait,
        ROUND(SUM(base_fare * surge_multiplier), 2) AS gross_booking_value,
        SUM(CASE WHEN surge_multiplier >= 1.5 THEN 1 ELSE 0 END) AS high_surge_requests_count
    FROM stg_ride_events
    GROUP BY
        city,
        date_hour_bucket,
        hour_of_day,
        day_of_week,
        day_name,
        is_weekend
),
city_thresholds AS (
    SELECT
        city,
        QUANTILE_CONT(total_requests, 0.85) AS p85_demand_threshold,
        MEDIAN(total_requests) AS median_demand_baseline,
        AVG(cancellation_rate_pct) AS baseline_cancellation_pct,
        STDDEV_POP(cancellation_rate_pct) AS stddev_cancellation_pct,
        AVG(acceptance_rate_pct) AS baseline_acceptance_pct
    FROM hourly_raw
    GROUP BY city
)
SELECT
    h.city,
    h.date_hour_bucket,
    h.hour_of_day,
    h.day_of_week,
    h.day_name,
    h.is_weekend,
    h.total_requests,
    h.accepted_requests,
    h.cancelled_requests,
    h.completed_trips,
    h.acceptance_rate_pct,
    h.cancellation_rate_pct,
    h.avg_surge,
    h.median_surge,
    h.avg_estimated_eta,
    h.avg_actual_wait,
    h.gross_booking_value,
    h.high_surge_requests_count,
    t.p85_demand_threshold,
    t.median_demand_baseline,
    t.baseline_cancellation_pct,
    COALESCE(t.stddev_cancellation_pct, 1.0) AS stddev_cancellation_pct,
    t.baseline_acceptance_pct,
    -- High Demand indicator based on city-specific P85 volume
    CASE WHEN h.total_requests >= t.p85_demand_threshold THEN 1 ELSE 0 END AS is_high_demand,
    -- Statistical Z-score for cancellation spike
    CASE 
        WHEN COALESCE(t.stddev_cancellation_pct, 0) > 0.001 
        THEN ROUND((h.cancellation_rate_pct - t.baseline_cancellation_pct) / t.stddev_cancellation_pct, 2)
        ELSE 0.0 
    END AS cancellation_z_score
FROM hourly_raw h
JOIN city_thresholds t ON h.city = t.city;
