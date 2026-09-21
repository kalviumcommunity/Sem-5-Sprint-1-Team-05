"""Core Analytical Engine & KPI Computations."""

from typing import Any

import pandas as pd

from src.database.executor import QueryExecutor


class KPIEngine:
    """Executes high-performance pushdown SQL analytics against DuckDB marts."""

    def __init__(self, executor: QueryExecutor | None = None):
        self.executor = executor or QueryExecutor()

    def get_global_executive_summary(self) -> dict[str, Any]:
        """Calculates global operational summary metrics."""
        sql = """
        SELECT
            SUM(total_requests_all) AS total_requests,
            SUM(high_demand_requests) AS high_demand_requests,
            ROUND(SUM(high_demand_requests) * 100.0 / NULLIF(SUM(total_requests_all), 0), 1) AS high_demand_share_pct,
            ROUND(AVG(normal_acceptance_pct), 1) AS global_normal_acceptance,
            ROUND(AVG(high_demand_acceptance_pct), 1) AS global_high_demand_acceptance,
            ROUND(AVG(normal_cancellation_pct), 1) AS global_normal_cancellation,
            ROUND(AVG(high_demand_cancellation_pct), 1) AS global_high_demand_cancellation,
            ROUND(AVG(normal_avg_surge), 2) AS global_normal_surge,
            ROUND(AVG(high_demand_avg_surge), 2) AS global_high_demand_surge,
            SUM(CASE WHEN operational_risk_status = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_cities_count,
            SUM(CASE WHEN operational_risk_status = 'WATCH' THEN 1 ELSE 0 END) AS watch_cities_count,
            SUM(CASE WHEN operational_risk_status = 'HEALTHY' THEN 1 ELSE 0 END) AS healthy_cities_count
        FROM mart_city_high_demand_summary;
        """
        df = self.executor.query_df(sql)
        if df.empty:
            return {}
        return df.iloc[0].to_dict()

    def get_city_summary_mart(self, city_filter: str | None = None) -> pd.DataFrame:
        """Fetches the city high-demand summary mart with optional filtering."""
        if city_filter and city_filter != "All":
            sql = "SELECT * FROM mart_city_high_demand_summary WHERE city = ? ORDER BY cancellation_delta_pp DESC;"
            return self.executor.query_df(sql, [city_filter])
        sql = "SELECT * FROM mart_city_high_demand_summary ORDER BY cancellation_delta_pp DESC;"
        return self.executor.query_df(sql)

    def get_city_hourly_trends(self, city: str) -> pd.DataFrame:
        """Fetches hourly timeline metrics for a specific city."""
        sql = """
        SELECT
            date_hour_bucket,
            hour_of_day,
            day_name,
            total_requests,
            accepted_requests,
            cancelled_requests,
            acceptance_rate_pct,
            cancellation_rate_pct,
            avg_surge,
            median_surge,
            is_high_demand,
            cancellation_z_score AS cancellation_zscore
        FROM fct_hourly_city_metrics
        WHERE city = ?
        ORDER BY date_hour_bucket ASC;
        """
        return self.executor.query_df(sql, [city])

    def get_city_risk_matrix_data(self) -> pd.DataFrame:
        """Fetches lightweight data payload for the City Risk Matrix visualization."""
        sql = """
        SELECT
            city,
            high_demand_acceptance_pct AS driver_acceptance_pct,
            high_demand_cancellation_pct AS rider_cancellation_pct,
            high_demand_requests AS demand_volume,
            high_demand_avg_surge AS surge_multiplier,
            operational_risk_status,
            consistency_pct,
            cancellation_delta_pp,
            acceptance_delta_pp
        FROM mart_city_high_demand_summary
        ORDER BY high_demand_cancellation_pct DESC;
        """
        return self.executor.query_df(sql)

    def get_top_operational_alerts(self, limit: int = 5) -> pd.DataFrame:
        """Fetches explainable alerts for cities showing highest deterioration."""
        sql = """
        SELECT
            city,
            operational_risk_status AS severity,
            normal_cancellation_pct,
            high_demand_cancellation_pct,
            cancellation_delta_pp,
            normal_acceptance_pct,
            high_demand_acceptance_pct,
            acceptance_delta_pp,
            high_demand_avg_surge,
            degraded_hd_periods,
            total_hd_periods,
            consistency_pct
        FROM mart_city_high_demand_summary
        WHERE operational_risk_status IN ('CRITICAL', 'WATCH')
        ORDER BY cancellation_delta_pp DESC
        LIMIT ?;
        """
        return self.executor.query_df(sql, [limit])


kpi_engine = KPIEngine()
