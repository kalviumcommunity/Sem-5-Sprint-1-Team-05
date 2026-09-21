"""Parameterized SQL query executor and query plan inspector."""

import time
from typing import Any

import duckdb
import pandas as pd

from src.database.connection import db_manager
from src.utils.logger import logger


class QueryExecutor:
    """Executes parameterized SQL queries against DuckDB with telemetry and safety checks."""

    def __init__(self, conn: duckdb.DuckDBPyConnection | None = None):
        self._conn = conn

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            return db_manager.get_connection()
        return self._conn

    def execute(self, sql: str, params: list[Any] | None = None) -> None:
        """Executes a non-returning DDL/DML query safely."""
        start_time = time.perf_counter()
        try:
            if params:
                self.conn.execute(sql, params)
            else:
                self.conn.execute(sql)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Executed SQL in {duration_ms:.2f}ms: {sql[:80]}...")
        except Exception as e:
            logger.error(f"SQL execution failure: {e} | Query: {sql}")
            raise

    def query_df(self, sql: str, params: list[Any] | None = None) -> pd.DataFrame:
        """Executes a SQL query and returns results directly as a Pandas DataFrame."""
        start_time = time.perf_counter()
        try:
            if params:
                df = self.conn.execute(sql, params).df()
            else:
                df = self.conn.execute(sql).df()
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Fetched {len(df)} rows in {duration_ms:.2f}ms | SQL: {sql[:80]}...")
            return df
        except Exception as e:
            logger.error(f"SQL query error: {e} | Query: {sql}")
            raise

    def explain(self, sql: str) -> str:
        """Returns the physical query plan for optimization analysis."""
        res = self.conn.execute(f"EXPLAIN {sql}").fetchall()
        return "\n".join([r[1] for r in res])
