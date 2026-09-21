-- Operational Anomalies Mart
CREATE OR REPLACE TABLE mart_operational_anomalies AS
SELECT
    f.city,
    f.date_hour_bucket,
    f.hour_of_day,
    f.day_name,
    f.is_high_demand,
    f.total_requests,
    f.cancellation_rate_pct,
    f.baseline_cancellation_pct,
    ROUND(f.cancellation_rate_pct - f.baseline_cancellation_pct, 2) AS cancellation_excess_pp,
    f.cancellation_z_score,
    f.acceptance_rate_pct,
    f.baseline_acceptance_pct,
    ROUND(f.acceptance_rate_pct - f.baseline_acceptance_pct, 2) AS acceptance_drop_pp,
    f.avg_surge,
    f.avg_actual_wait,
    CASE
        WHEN f.cancellation_z_score >= 3.0 OR f.avg_surge >= 2.50 THEN 'SEVERE_ANOMALY'
        WHEN f.cancellation_z_score >= 2.0 OR f.avg_surge >= 2.00 THEN 'MODERATE_ANOMALY'
        ELSE 'NORMAL'
    END AS anomaly_severity
FROM fct_hourly_city_metrics f
WHERE f.cancellation_z_score >= 2.0 OR f.avg_surge >= 2.20
ORDER BY f.cancellation_z_score DESC, f.date_hour_bucket DESC;
