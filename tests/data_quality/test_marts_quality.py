"""Data quality tests for analytical marts."""

from src.database.executor import QueryExecutor


def test_marts_no_null_keys():
    executor = QueryExecutor()
    df = executor.query_df("SELECT * FROM mart_city_high_demand_summary WHERE city IS NULL;")
    assert len(df) == 0


def test_rates_bounded():
    executor = QueryExecutor()
    df = executor.query_df("""
        SELECT * FROM mart_city_high_demand_summary 
        WHERE normal_acceptance_pct < 0 OR normal_acceptance_pct > 100
           OR high_demand_acceptance_pct < 0 OR high_demand_acceptance_pct > 100
           OR normal_cancellation_pct < 0 OR normal_cancellation_pct > 100
           OR high_demand_cancellation_pct < 0 OR high_demand_cancellation_pct > 100;
    """)
    assert len(df) == 0


def test_consistency_bounded():
    executor = QueryExecutor()
    df = executor.query_df("""
        SELECT * FROM mart_city_high_demand_summary
        WHERE consistency_pct < 0.0 OR consistency_pct > 100.0;
    """)
    assert len(df) == 0
