"""Statistical Association & Correlation Engine."""

from typing import Any

import pandas as pd
from scipy import stats

from src.database.executor import QueryExecutor


class CorrelationEngine:
    """Calculates statistical relationships between acceptance, surge, demand, and cancellation."""

    def __init__(self, executor: QueryExecutor = None):
        self.executor = executor or QueryExecutor()

    def get_hourly_correlation_matrix(self) -> dict[str, Any]:
        """Computes Pearson & Spearman correlation coefficients across operational metrics."""
        sql = """
        SELECT
            acceptance_rate_pct,
            cancellation_rate_pct,
            avg_surge,
            total_requests,
            avg_actual_wait
        FROM fct_hourly_city_metrics;
        """
        df = self.executor.query_df(sql)
        if df.empty or len(df) < 5:
            return {"pearson": pd.DataFrame(), "spearman": pd.DataFrame(), "p_values": {}}

        pearson_corr = df.corr(method="pearson").round(3)
        spearman_corr = df.corr(method="spearman").round(3)

        # Calculate p-value between driver acceptance and rider cancellation
        acc_canc_stat = stats.pearsonr(df["acceptance_rate_pct"], df["cancellation_rate_pct"])
        surge_canc_stat = stats.pearsonr(df["avg_surge"], df["cancellation_rate_pct"])

        return {
            "pearson": pearson_corr,
            "spearman": spearman_corr,
            "acceptance_vs_cancellation_r": round(float(acc_canc_stat.statistic), 3),
            "acceptance_vs_cancellation_p": float(acc_canc_stat.pvalue),
            "surge_vs_cancellation_r": round(float(surge_canc_stat.statistic), 3),
            "surge_vs_cancellation_p": float(surge_canc_stat.pvalue),
            "sample_size": len(df),
        }


correlation_engine = CorrelationEngine()
