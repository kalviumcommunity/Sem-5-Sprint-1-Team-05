"""Cached Database & Query Service for Streamlit."""

import time
from typing import Any

import duckdb
import pandas as pd
import streamlit as st

from src.analytics.anomalies import anomaly_engine
from src.analytics.correlations import correlation_engine
from src.analytics.kpi_engine import kpi_engine
from src.config.settings import settings


@st.cache_resource
def get_db_connection() -> duckdb.DuckDBPyConnection:
    """Returns persistent cached DuckDB read connection."""
    return duckdb.connect(str(settings.DUCKDB_PATH), read_only=True)


@st.cache_data(ttl=300)
def fetch_global_summary() -> tuple[dict[str, Any], float]:
    """Cached fetch of global KPIs with execution latency."""
    t0 = time.perf_counter()
    res = kpi_engine.get_global_executive_summary()
    lat_ms = (time.perf_counter() - t0) * 1000
    return res, lat_ms


@st.cache_data(ttl=300)
def fetch_city_summary(city_filter: str | None = None) -> tuple[pd.DataFrame, float]:
    """Cached fetch of city high-demand summary mart."""
    t0 = time.perf_counter()
    df = kpi_engine.get_city_summary_mart(city_filter)
    lat_ms = (time.perf_counter() - t0) * 1000
    return df, lat_ms


@st.cache_data(ttl=300)
def fetch_city_trends(city: str) -> tuple[pd.DataFrame, float]:
    """Cached fetch of city hourly timeline metrics."""
    t0 = time.perf_counter()
    df = kpi_engine.get_city_hourly_trends(city)
    lat_ms = (time.perf_counter() - t0) * 1000
    return df, lat_ms


@st.cache_data(ttl=300)
def fetch_risk_matrix_data() -> tuple[pd.DataFrame, float]:
    """Cached fetch of city risk matrix payload."""
    t0 = time.perf_counter()
    df = kpi_engine.get_city_risk_matrix_data()
    lat_ms = (time.perf_counter() - t0) * 1000
    return df, lat_ms


@st.cache_data(ttl=300)
def fetch_top_alerts(limit: int = 5) -> tuple[pd.DataFrame, float]:
    """Cached fetch of top operational alerts."""
    t0 = time.perf_counter()
    df = kpi_engine.get_top_operational_alerts(limit)
    lat_ms = (time.perf_counter() - t0) * 1000
    return df, lat_ms


@st.cache_data(ttl=300)
def fetch_correlation_data() -> tuple[dict[str, Any], float]:
    """Cached fetch of correlation statistics."""
    t0 = time.perf_counter()
    res = correlation_engine.get_hourly_correlation_matrix()
    lat_ms = (time.perf_counter() - t0) * 1000
    return res, lat_ms


@st.cache_data(ttl=300)
def fetch_anomalies(city_filter: str | None = None, limit: int = 50) -> tuple[pd.DataFrame, float]:
    """Cached fetch of operational anomalies."""
    t0 = time.perf_counter()
    df = anomaly_engine.get_anomalies(city_filter, limit)
    lat_ms = (time.perf_counter() - t0) * 1000
    return df, lat_ms
