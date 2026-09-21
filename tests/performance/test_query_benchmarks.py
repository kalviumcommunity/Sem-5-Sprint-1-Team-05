"""Performance benchmark tests ensuring sub-50ms execution times."""

import time

from src.database.executor import QueryExecutor


def test_analytical_query_performance():
    executor = QueryExecutor()
    queries = [
        "SELECT * FROM mart_city_high_demand_summary;",
        "SELECT * FROM fct_hourly_city_metrics WHERE is_high_demand = 1;",
        "SELECT * FROM mart_operational_anomalies LIMIT 50;",
    ]

    for q in queries:
        t0 = time.perf_counter()
        _ = executor.query_df(q)
        latency_ms = (time.perf_counter() - t0) * 1000
        assert latency_ms < 50.0, (
            f"Query '{q[:30]}...' took {latency_ms:.2f}ms (exceeded 50ms budget)"
        )
