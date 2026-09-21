# Ride-Sharing Operational Intelligence Platform

> A production-ready data engineering and operational intelligence platform for identifying city-level marketplace strain during high-demand periods.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![DuckDB](https://img.shields.io/badge/DuckDB-1.0%2B-yellow.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Overview

Ride-sharing operations teams need to know where rider experience breaks down, when it happens, and which operational behaviors are associated with the breakdown. This project turns ride request events into validated hourly metrics, city-level risk summaries, anomaly logs, and deterministic operational diagnoses.

The reference scenario processes more than 400,000 synthetic events across eight metropolitan markets. The architecture is designed so the synthetic source can later be replaced with a production event source without changing the dashboard metric contracts.

## What the Platform Answers

| Question | Answer provided by the platform |
| --- | --- |
| Where? | Which cities have the highest operational risk during peak demand? |
| What? | Which driver, rider, pricing, and wait-time signals move with the deterioration? |
| When? | Which hours, weekdays, and demand windows show recurring friction? |
| Why? | What changed between normal and high-demand periods? |
| How consistently? | Is the problem a one-off anomaly or a recurring structural capacity issue? |

## Key Capabilities

- Deterministic synthetic ride-event generation for repeatable development and testing.
- Data quality gates for required fields, duplicates, value bounds, and state consistency.
- City-specific P85 demand classification rather than a biased global volume threshold.
- DuckDB analytical marts at hourly city grain.
- KPI, correlation, anomaly, and deterministic diagnosis engines.
- Five-page Streamlit dashboard for executive and operational investigation.
- Cached analytical queries designed for interactive dashboard use.
- No direct personal identifiers in the analytical model.

## Architecture

```text
Raw CSV or generated events
          |
          v
Ingestion -> Validation -> Cleaning and feature extraction
          |
          v
DuckDB staging tables
          |
          +--> fct_hourly_city_metrics
          +--> mart_city_high_demand_summary
          +--> mart_operational_anomalies
          |
          v
Analytics layer -> Cached Streamlit data service -> Five dashboard pages
```

## Repository Structure

```text
data/                 Raw and processed data artifacts
src/config/           Settings and thresholds
src/validation/       Data quality checks and schemas
src/transformation/   Cleaning and temporal feature extraction
src/ingestion/        Data generator and pipeline orchestrator
src/database/         DuckDB connection and query execution
src/analytics/        KPIs, diagnosis, correlations, and anomalies
sql/schema/           Staging table definitions
sql/marts/            Analytical mart SQL
dashboard/            Streamlit app, pages, components, and styling
tests/                Unit, integration, quality, and performance tests
docs/                 Architecture, methodology, assumptions, and PRD
```

## Quickstart

### Prerequisites

- Python 3.10 or newer
- Git

### Install

```bash
git clone <repository-url>
cd sprint-4

python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
# source .venv/bin/activate

pip install -e ".[dev]"
```

### Generate Data and Build Marts

```bash
python -c "from src.ingestion.pipeline import pipeline; pipeline.run(force_regenerate=True)"
```

This creates the raw CSV, cleaned parquet backup, DuckDB database, and analytical marts.

### Start the Dashboard

```bash
streamlit run dashboard/app.py
```

Open http://localhost:8501 in a browser.

## Dashboard Pages

1. **Executive Overview** - Global KPIs, alerts, and city risk comparison.
2. **City Intelligence** - City-level hourly demand and operational trends.
3. **High Demand Analysis** - Peak-versus-baseline behavior and associations.
4. **Operational Diagnosis** - Deterministic root-cause breakdown and anomaly log.
5. **Data Quality Health** - Validation status and analytical data health.

## Testing

Run the complete test suite from the project root:

```bash
pytest
```

If running directly from a checkout without editable installation, set the project root on `PYTHONPATH` first:

```powershell
$env:PYTHONPATH = (Get-Location).Path
pytest
```

## Docker

```bash
docker build -t ride-sharing-ops:latest .
docker run -p 8501:8501 ride-sharing-ops:latest
```

## Documentation

- [Product Requirements Document](docs/product_requirements.md)
- [UX Submission](docs/ux_submission.md)
- [Architecture](docs/architecture.md)
- [Analytical Methodology](docs/analytical_methodology.md)
- [Data Dictionary](docs/data_dictionary.md)
- [Assumptions](docs/assumptions.md)
- [Architecture Decisions](docs/decisions.md)
- [Performance Notes](docs/performance.md)
- [Security Controls](docs/security.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
