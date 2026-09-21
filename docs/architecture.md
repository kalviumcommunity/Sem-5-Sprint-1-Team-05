# Architecture Specification — Ride-Sharing Operational Intelligence Platform

## 1. System Overview

The Ride-Sharing Operational Intelligence Platform transforms high-frequency ride request event telemetry into sub-second actionable intelligence for market operations teams.

```
RAW EVENT STREAM / CSV
        │
        ▼
[ Ingestion & Data Generator ] ──► [ Data Quality Auditor (Pydantic / Pandera) ]
                                                │
                                                ▼
                                    [ Clean & Feature Extraction ]
                                                │
                                                ▼
                                    [ DuckDB Columnar OLAP Engine ]
                                                │
       ┌────────────────────────────────────────┼────────────────────────────────────────┐
       ▼                                        ▼                                        ▼
[ fct_hourly_city_metrics ]      [ mart_city_high_demand_summary ]        [ mart_operational_anomalies ]
       │                                        │                                        │
       └────────────────────────────────────────┼────────────────────────────────────────┘
                                                │
                                                ▼
                                 [ Pushdown SQL Query Layer ]
                                                │
                                                ▼
                             [ Streamlit Cached Data Service (TTL 300s) ]
                                                │
                                                ▼
                             [ 5-Page Interactive Operational UI ]
```

## 2. Layered Responsibilities

### Ingestion & Validation Layer (`src/ingestion/`, `src/validation/`)
- Ingests raw event logs.
- Executes automated data quality gate inspections checking null frequencies, duplicate identifiers, state consistency, and range constraints.
- Quarantines malformed records and logs actionable quality reports.

### Transformation Layer (`src/transformation/`)
- Sanitizes entity attributes (e.g. city normalization).
- Extracts temporal dimensions (hour bucket, day of week, rush-hour indicators).
- Enforces state integrity (e.g., mutually exclusive completed vs. cancelled trip states).

### Storage & Marts Layer (`src/database/`, `sql/`)
- Leverages in-process vectorized columnar storage in **DuckDB**.
- Builds pre-aggregated hourly facts and high-demand baseline comparative data marts.
- Materializes statistical anomaly flags ($Z \ge 2.0$) directly in analytical storage.

### Analytics & Diagnostics Engine (`src/analytics/`)
- Provides pushdown SQL aggregations.
- Computes mathematical correlations (Pearson, Spearman) and effect sizes.
- Generates **deterministic, evidence-based natural language diagnoses** without hallucination or hardcoded statements.

### UI & Visualization Layer (`dashboard/`)
- Modern, glassmorphic Streamlit interface.
- 4D City Operational Risk Matrix with Plotly integration.
- Sub-50ms query response times via `@st.cache_data` and DuckDB C++ execution.
