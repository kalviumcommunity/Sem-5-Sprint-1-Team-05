"""Statistical Anomaly Detection Engine."""

import pandas as pd

from src.database.executor import QueryExecutor


class AnomalyEngine:
    """Queries and formats operational anomalies identified in the data marts."""

    def __init__(self, executor: QueryExecutor | None = None):
        self.executor = executor or QueryExecutor()

    def get_anomalies(self, city_filter: str | None = None, limit: int = 50) -> pd.DataFrame:
        """Retrieves flagged statistical anomalies."""
        if city_filter and city_filter != "All":
            sql = """
            SELECT
                city,
                date_hour_bucket,
                hour_of_day,
                day_name,
                is_high_demand,
                total_requests,
                cancellation_rate_pct,
                baseline_cancellation_pct,
                cancellation_excess_pp,
                cancellation_z_score,
                acceptance_rate_pct,
                acceptance_drop_pp,
                avg_surge,
                anomaly_severity
            FROM mart_operational_anomalies
            WHERE city = ?
            ORDER BY cancellation_z_score DESC
            LIMIT ?;
            """
            return self.executor.query_df(sql, [city_filter, limit])

        sql = """
        SELECT
            city,
            date_hour_bucket,
            hour_of_day,
            day_name,
            is_high_demand,
            total_requests,
            cancellation_rate_pct,
            baseline_cancellation_pct,
            cancellation_excess_pp,
            cancellation_z_score,
            acceptance_rate_pct,
            acceptance_drop_pp,
            avg_surge,
            anomaly_severity
        FROM mart_operational_anomalies
        ORDER BY cancellation_z_score DESC
        LIMIT ?;
        """
        return self.executor.query_df(sql, [limit])


anomaly_engine = AnomalyEngine()
