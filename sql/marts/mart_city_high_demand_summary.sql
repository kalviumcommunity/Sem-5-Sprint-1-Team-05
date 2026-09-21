-- City-Level High-Demand vs. Normal Baseline Mart
CREATE OR REPLACE TABLE mart_city_high_demand_summary AS
WITH regime_stats AS (
    SELECT
        city,
        is_high_demand,
        COUNT(*) AS period_count,
        SUM(total_requests) AS total_requests,
        SUM(accepted_requests) AS accepted_requests,
        SUM(cancelled_requests) AS cancelled_requests,
        ROUND(AVG(acceptance_rate_pct), 2) AS avg_acceptance_rate,
        ROUND(AVG(cancellation_rate_pct), 2) AS avg_cancellation_rate,
        ROUND(AVG(avg_surge), 2) AS avg_surge_multiplier,
        ROUND(MEDIAN(median_surge), 2) AS median_surge_multiplier,
        ROUND(AVG(avg_actual_wait), 1) AS avg_wait_time_min,
        SUM(high_surge_requests_count) AS total_high_surge_requests
    FROM fct_hourly_city_metrics
    GROUP BY city, is_high_demand
),
normal_baseline AS (
    SELECT * FROM regime_stats WHERE is_high_demand = 0
),
high_demand AS (
    SELECT * FROM regime_stats WHERE is_high_demand = 1
),
consistency_calc AS (
    -- Operationalize "Consistency": fraction of high demand periods with degraded cancellation
    SELECT
        f.city,
        COUNT(*) AS total_hd_periods,
        SUM(CASE WHEN f.cancellation_rate_pct >= (n.avg_cancellation_rate + 4.0) THEN 1 ELSE 0 END) AS degraded_hd_periods,
        ROUND(
            SUM(CASE WHEN f.cancellation_rate_pct >= (n.avg_cancellation_rate + 4.0) THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0),
            1
        ) AS consistency_pct
    FROM fct_hourly_city_metrics f
    JOIN normal_baseline n ON f.city = n.city
    WHERE f.is_high_demand = 1
    GROUP BY f.city
)
SELECT
    n.city,
    (n.total_requests + COALESCE(h.total_requests, 0)) AS total_requests_all,
    COALESCE(h.total_requests, 0) AS high_demand_requests,
    ROUND(COALESCE(h.total_requests, 0) * 100.0 / NULLIF((n.total_requests + COALESCE(h.total_requests, 0)), 0), 1) AS high_demand_request_share_pct,
    
    -- Normal Baseline KPIs
    n.avg_acceptance_rate AS normal_acceptance_pct,
    n.avg_cancellation_rate AS normal_cancellation_pct,
    n.avg_surge_multiplier AS normal_avg_surge,
    n.median_surge_multiplier AS normal_median_surge,
    n.avg_wait_time_min AS normal_wait_time_min,
    
    -- High Demand KPIs
    COALESCE(h.avg_acceptance_rate, n.avg_acceptance_rate) AS high_demand_acceptance_pct,
    COALESCE(h.avg_cancellation_rate, n.avg_cancellation_rate) AS high_demand_cancellation_pct,
    COALESCE(h.avg_surge_multiplier, n.avg_surge_multiplier) AS high_demand_avg_surge,
    COALESCE(h.median_surge_multiplier, n.median_surge_multiplier) AS high_demand_median_surge,
    COALESCE(h.avg_wait_time_min, n.avg_wait_time_min) AS high_demand_wait_time_min,
    
    -- Deterioration Deltas (pp = percentage points)
    ROUND(COALESCE(h.avg_acceptance_rate, n.avg_acceptance_rate) - n.avg_acceptance_rate, 2) AS acceptance_delta_pp,
    ROUND(COALESCE(h.avg_cancellation_rate, n.avg_cancellation_rate) - n.avg_cancellation_rate, 2) AS cancellation_delta_pp,
    ROUND(COALESCE(h.avg_surge_multiplier, n.avg_surge_multiplier) - n.avg_surge_multiplier, 2) AS surge_delta,
    ROUND(COALESCE(h.avg_wait_time_min, n.avg_wait_time_min) - n.avg_wait_time_min, 1) AS wait_time_delta_min,
    
    -- Consistency Quantification
    c.total_hd_periods,
    c.degraded_hd_periods,
    COALESCE(c.consistency_pct, 0.0) AS consistency_pct,
    
    -- Operational Segmentation Classification
    CASE
        WHEN (COALESCE(h.avg_cancellation_rate, n.avg_cancellation_rate) - n.avg_cancellation_rate >= 8.0 
              OR n.avg_acceptance_rate - COALESCE(h.avg_acceptance_rate, n.avg_acceptance_rate) >= 15.0)
             AND COALESCE(c.consistency_pct, 0.0) >= 50.0 THEN 'CRITICAL'
        WHEN (COALESCE(h.avg_cancellation_rate, n.avg_cancellation_rate) - n.avg_cancellation_rate >= 4.0
              OR n.avg_acceptance_rate - COALESCE(h.avg_acceptance_rate, n.avg_acceptance_rate) >= 8.0) THEN 'WATCH'
        ELSE 'HEALTHY'
    END AS operational_risk_status
FROM normal_baseline n
LEFT JOIN high_demand h ON n.city = h.city
LEFT JOIN consistency_calc c ON n.city = c.city;
