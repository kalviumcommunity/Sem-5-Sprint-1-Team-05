# Product Requirements Document
## Ride-Sharing Operational Intelligence Platform

**Document status:** Baseline PRD for the current implemented product
**Version:** 1.0
**Date:** 2026-09-21
**Product owner:** Mobility Operations and Data Engineering
**Primary users:** City operations leaders, marketplace managers, supply operations analysts, data quality owners, and engineering reviewers

---

## 1. Product Summary

The Ride-Sharing Operational Intelligence Platform converts ride request event telemetry into an operational view of marketplace strain. It helps mobility operations teams identify which cities are degrading during high-demand periods, determine when the degradation occurs, quantify the behavioral drivers, and decide where intervention is warranted.

The product combines an ingestion and validation pipeline, deterministic analytical models, DuckDB data marts, and a five-page Streamlit dashboard. It is designed for fast, repeatable investigation rather than real-time dispatch control.

The current implementation uses deterministic synthetic ride-sharing events to demonstrate the complete product workflow. The same contracts are intended to support replacement with production event data after source integration and governance work are completed.

### Product promise

> Give operations leaders a defensible answer to: where is rider experience breaking down, when does it happen, what behavior is associated with the breakdown, and how consistently should we intervene?

---

## 2. Problem Statement

Ride-sharing marketplaces generate large volumes of dispatch, acceptance, cancellation, pricing, and wait-time events. Raw event volume alone does not tell an operations leader whether a market has a temporary spike or a recurring capacity problem.

Without a unified analytical product, teams face four problems:

1. **Risk is difficult to localize.** Absolute request volume unfairly favors large markets and hides strain in smaller markets.
2. **Peak behavior is difficult to compare.** Normal and high-demand periods are often mixed together, obscuring deterioration.
3. **Root cause is difficult to communicate.** A dashboard may show a cancellation rate without showing whether acceptance, wait time, or surge changed first.
4. **Trust is difficult to maintain.** Unvalidated data, unclear metric definitions, and ungrounded narratives reduce confidence in operational decisions.

The platform addresses these problems through city-specific percentile thresholds, hourly aggregation, baseline-vs-peak comparisons, deterministic diagnoses, and visible data-quality controls.

---

## 3. Goals and Success Measures

### 3.1 Product goals

- Provide a single operational view of city-level marketplace health.
- Identify recurring high-demand degradation instead of isolated noise.
- Compare normal and high-demand behavior using transparent metrics.
- Surface evidence-backed operational diagnoses without invented facts.
- Make data quality and analytical assumptions inspectable.
- Keep investigation fast enough for interactive dashboard use.
- Allow the complete workflow to run locally without an external database server.

### 3.2 Success measures

| Measure | Target | Validation method |
|---|---:|---|
| Dataset processing | 400,000+ events in the reference scenario | Pipeline result and row-count audit |
| Pipeline completion | 100% successful run on valid reference data | Integration test |
| Data quality | Quality gate score of 100% for reference data | Quality report |
| Analytical query latency | Sub-50 ms target for dashboard queries | Performance test and dashboard telemetry |
| Anomaly identification | Detect qualifying cancellation or surge anomalies | Mart quality tests and page verification |
| Diagnosis reproducibility | Same input metrics produce the same narrative | Unit tests |
| Dashboard coverage | Five operational pages available | Manual smoke test |
| Identifier protection | No names, phone numbers, payment tokens, or raw PII in marts | Schema and security review |

### 3.3 Business outcomes

- Faster escalation of structurally constrained markets.
- Better prioritization of driver supply and marketplace interventions.
- Shared definitions for peak demand, deterioration, and operational risk.
- Less manual spreadsheet analysis and fewer unsupported causal claims.

---

## 4. Non-Goals

The following are explicitly outside the current product scope:

- Real-time dispatch, driver assignment, or pricing decisions.
- Automated driver or rider communication.
- Predictive demand forecasting or staffing recommendations.
- Individual driver performance management.
- Customer-facing rider experience reporting.
- Revenue accounting, payment processing, or fare settlement.
- Storage of personally identifiable information.
- LLM-generated diagnosis or free-form causal claims.
- Multi-user authentication, role-based access control, or hosted tenancy.
- Guaranteed production streaming ingestion; the current reference workflow uses CSV input and deterministic synthetic generation.

---

## 5. Users and Personas

### 5.1 City Operations Leader

**Need:** Quickly identify which market requires attention and understand the operational reason.

**Typical questions:**
- Which cities are critical today or in the observed window?
- Is the problem recurring or isolated?
- Is driver supply, rider cancellation, wait time, or pricing the dominant signal?
- What action should the city team investigate first?

**Primary surfaces:** Executive Overview, City Intelligence, Operational Diagnosis.

### 5.2 Marketplace or Supply Operations Analyst

**Need:** Investigate hourly patterns and compare cities or time windows.

**Typical questions:**
- Which hours and days show peak friction?
- How large is the acceptance drop during high demand?
- Does elevated surge co-occur with cancellations?
- Which markets have similar operational signatures?

**Primary surfaces:** City Intelligence, High Demand Analysis, Operational Diagnosis.

### 5.3 Data Quality Owner

**Need:** Confirm that analytical outputs are based on complete, valid, and internally consistent data.

**Typical questions:**
- Are required fields present and within bounds?
- Are request IDs unique?
- Are completed and cancelled states consistent?
- Are marts populated and bounded?

**Primary surface:** Data Quality Health.

### 5.4 Engineering or Analytics Reviewer

**Need:** Validate that the product is reproducible, performant, secure, and maintainable.

**Typical questions:**
- Can the pipeline be rerun from a clean checkout?
- Are metrics defined and testable?
- Are SQL queries parameterized?
- Do results match the documented methodology?

**Primary surfaces:** Repository, documentation, tests, and all dashboard pages.

---

## 6. Core User Journeys

### Journey A: Executive risk scan

1. User opens Executive Overview.
2. User reviews global request volume, cancellation, acceptance, surge, and risk indicators.
3. User identifies the highest-risk markets in the operational risk matrix.
4. User opens the affected market in City Intelligence or Operational Diagnosis.
5. User records the market and evidence for follow-up.

**Expected outcome:** The user can identify the highest-priority markets without inspecting raw events.

### Journey B: City investigation

1. User selects a city.
2. User reviews its hourly demand and performance trend.
3. User compares normal and high-demand rates.
4. User checks whether the deterioration repeats across high-demand windows.
5. User opens the diagnosis panel for the dominant change and recommended operational focus.

**Expected outcome:** The user can distinguish recurring structural strain from a one-hour anomaly.

### Journey C: Root-cause and anomaly review

1. User opens Operational Diagnosis.
2. User selects a target metro.
3. User reviews acceptance, cancellation, surge, and consistency deltas.
4. User reads the deterministic narrative and recommended operational fix.
5. User reviews the statistical anomaly incident log for supporting hourly evidence.

**Expected outcome:** The user gets a traceable explanation grounded in computed metrics.

### Journey D: Data trust check

1. User opens Data Quality Health.
2. User reviews quality score and failed checks, if any.
3. User verifies row counts, null checks, uniqueness, state consistency, and mart health.
4. User decides whether dashboard results are fit for operational use.

**Expected outcome:** Users can identify whether a conclusion is blocked by data quality.

---

## 7. Functional Requirements

### FR-1: Data ingestion

- The system shall accept a ride event dataset with the documented staging schema.
- The system shall generate a deterministic synthetic reference dataset when raw input is absent or regeneration is requested.
- The reference generator shall support a configurable start date, number of days, and random seed.
- The pipeline shall write raw input to `data/raw/ride_events_raw.csv` when generation is used.
- The pipeline shall report raw row count and clean row count.
- The pipeline shall return an explicit success status on completion.

### FR-2: Data quality gates

- The system shall validate required columns before transformation.
- The system shall detect duplicate request identifiers.
- The system shall validate numeric bounds and expected binary states.
- The system shall detect invalid combinations of accepted, cancelled, and completed states.
- The system shall report a quality status and score.
- The pipeline shall preserve an auditable quality report for the run or expose it to the application layer.
- Invalid data shall not silently appear as valid analytical output.

### FR-3: Transformation and feature extraction

- The system shall normalize city and entity attributes according to the transformation rules.
- The system shall derive hourly buckets from event timestamps.
- The system shall derive hour of day, day of week, day name, and weekend indicator.
- The system shall enforce the documented trip-state consistency rules.
- The system shall write cleaned records to the processed parquet artifact.

### FR-4: Analytical storage and marts

- The system shall load cleaned events into the DuckDB staging table.
- The system shall materialize `fct_hourly_city_metrics`.
- The system shall materialize `mart_city_high_demand_summary`.
- The system shall materialize `mart_operational_anomalies`.
- Marts shall expose stable names and columns documented in the data dictionary.
- Re-running the pipeline shall replace or refresh derived tables without creating duplicate records.
- Analytical queries shall use parameterized values where filters are supplied by the application.

### FR-5: High-demand classification

- The system shall calculate demand thresholds independently for each city.
- High demand shall be defined using the city-specific 85th percentile of hourly request volume.
- The system shall expose whether an hourly period is high demand.
- The classification shall not use a single global request-volume threshold.
- The methodology shall be visible in documentation and understandable to an operational reviewer.

### FR-6: Executive Overview

The Executive Overview shall:

- Display global request, acceptance, cancellation, surge, and risk indicators.
- Surface the most important operational alerts.
- Present a city-level risk matrix or equivalent comparison view.
- Allow the user to identify critical, watch, and healthy markets.
- Link the user conceptually to deeper city and diagnosis views.

### FR-7: City Intelligence

The City Intelligence page shall:

- Provide a city selector.
- Display hourly city trends.
- Show demand volume alongside operational rates.
- Make rush-hour and weekend patterns inspectable.
- Support comparison of normal and high-demand behavior.
- Preserve consistent metric definitions with the marts and diagnosis page.

### FR-8: High Demand Analysis

The High Demand Analysis page shall:

- Show the high-demand methodology and city-level results.
- Compare peak behavior with baseline behavior.
- Show relevant association or correlation evidence.
- Identify markets where driver acceptance and rider cancellation move in the most concerning direction.
- Avoid presenting correlation as proof of causation.

### FR-9: Operational Diagnosis

The Operational Diagnosis page shall:

- Allow a city to be selected.
- Show risk classification and consistency percentage.
- Show acceptance, cancellation, and surge deltas.
- Show baseline and high-demand values for the primary metrics.
- Generate a deterministic narrative from computed values.
- Provide an operational recommendation based on the dominant measured change.
- Show hourly anomaly incidents with city, timestamp, cancellation rate, cancellation Z-score, acceptance rate, surge, volume, and severity.
- Handle an empty anomaly result without rendering an application error.

### FR-10: Data Quality Health

The Data Quality Health page shall:

- Show the latest quality status and score.
- Show key validation checks and failures.
- Show row or table health for the analytical layer.
- Make data-quality failures visible before users rely on operational conclusions.

### FR-11: Correlation and diagnosis behavior

- The system shall calculate documented Pearson and Spearman associations where supported by the analytics layer.
- The system shall report effect metrics with their relevant time grain and population.
- Diagnostic narratives shall be deterministic and based only on computed metrics.
- Diagnostic text shall not invent percentages, cities, causes, or recommendations absent from the underlying inputs.
- The application shall distinguish association from causation in user-facing context.

### FR-12: Anomaly detection

- The system shall flag hourly periods where cancellation Z-score is at least 2.0 or average surge reaches the documented anomaly threshold.
- The system shall assign severity using the documented cancellation and surge thresholds.
- The anomaly log shall be sortable or ordered by severity/evidence according to the current query contract.
- Anomaly output shall retain the originating city and hour for investigation.

---

## 8. Metric Definitions and Rules

| Metric | Definition | Product use |
|---|---|---|
| Driver acceptance rate | Accepted requests / total requests * 100 | Supply responsiveness |
| Rider cancellation rate | Cancelled requests / total requests * 100 | Rider friction |
| Surge multiplier | Mean or median dynamic fare multiplier for the period | Price pressure |
| Acceptance delta | High-demand acceptance - normal acceptance | Peak supply deterioration |
| Cancellation delta | High-demand cancellation - normal cancellation | Peak rider friction |
| Surge delta | High-demand surge - normal surge | Peak pricing change |
| Degraded high-demand period | Cancellation rate exceeds normal baseline by at least 4 percentage points | Consistency calculation |
| Consistency percentage | Degraded high-demand periods / total high-demand periods * 100 | Structural risk evidence |
| Cancellation Z-score | Cancellation deviation from baseline divided by baseline standard deviation | Hourly anomaly detection |
| Critical city | Consistency and delta thresholds defined in settings are met | Executive prioritization |

### Risk classification rule

A market is classified as `CRITICAL`, `WATCH`, or `HEALTHY` using the configured risk thresholds. The product must display the classification together with the underlying deltas and consistency so that the label is explainable.

### Interpretation rule

The product may state that driver unacceptance is associated with higher cancellation or that the metrics move together. It shall not state that one metric definitively causes another without a separate causal design.

---

## 9. Data and Technical Requirements

### 9.1 Reference data scope

- Eight reference cities: Mumbai, Delhi, Bengaluru, Hyderabad, Chennai, Singapore, London, and New York.
- Reference observation window: 14 days beginning 2026-08-01 UTC.
- Reference event volume: approximately 408,000 records.
- Event grain: one ride request event.
- Analytical grain: one city-hour for fact metrics.

### 9.2 Required staging fields

The staging contract shall include request ID, city, timestamp, driver ID, driver acceptance, rider cancellation, cancellation reason, surge multiplier, base fare, estimated ETA, actual wait time, trip completion, and trip distance. Derived temporal fields shall be present after cleaning.

### 9.3 Storage

- DuckDB is the local analytical engine.
- CSV is the raw reference interchange format.
- Parquet is the cleaned processed backup format.
- SQL files are the source of truth for staging and marts.
- The dashboard shall read derived data through the query/analytics layer rather than duplicating SQL in page code.

### 9.4 Reproducibility

- A clean environment shall be able to install dependencies from `pyproject.toml`.
- The pipeline shall be rerunnable from the documented command.
- Synthetic data generation shall be deterministic for the same seed and parameters.
- Tests shall verify quality, diagnosis, pipeline integration, and query performance.

---

## 10. Non-Functional Requirements

### Performance

- Dashboard reads should target sub-50 ms query execution for common analytical views.
- Pipeline performance should remain suitable for the reference dataset on a developer workstation.
- Dashboard data shall use caching with a bounded TTL, currently 300 seconds.

### Reliability

- A failed quality gate shall be visible and actionable.
- Missing or empty mart results shall render a controlled empty state rather than a traceback.
- The application shall fail with a useful message when the database has not been generated.
- Pipeline reruns shall be idempotent at the mart level.

### Security and privacy

- Secrets shall be read from environment configuration and never committed.
- `.env.example` shall document required configuration without containing secrets.
- SQL filters shall be parameterized.
- Analytical data shall use surrogate IDs and shall not contain names, phone numbers, payment tokens, or other direct personal identifiers.
- Production containers shall run as a non-root user.

### Usability

- Users shall understand the meaning of risk labels from nearby evidence.
- Metric names and units shall be consistent across pages.
- Time windows, city selection, and high-demand status shall be visible in context.
- Errors shall identify the affected page or data layer and suggest the next action.
- The dashboard shall remain usable at common desktop viewport sizes.

### Maintainability

- Business logic shall remain in `src/`, SQL, or shared dashboard utilities rather than being duplicated across pages.
- Public metric and mart contracts shall be documented.
- New data sources shall be able to implement the staging contract without rewriting every dashboard page.
- Changes to threshold definitions shall be centralized in configuration.

---

## 11. Acceptance Criteria

### End-to-end acceptance

- [ ] A clean environment can install the declared dependencies.
- [ ] The pipeline generates or loads raw events successfully.
- [ ] The quality gate reports status and score.
- [ ] Clean parquet and DuckDB outputs are written.
- [ ] All three marts are populated.
- [ ] The Streamlit application starts and serves all five pages.
- [ ] The dashboard can display data after a successful pipeline run.

### Analytical acceptance

- [ ] High-demand classification is city-specific P85.
- [ ] Normal-vs-peak deltas match the documented formulas.
- [ ] Consistency uses degraded high-demand periods divided by total high-demand periods.
- [ ] Anomaly results expose the documented Z-score field and severity.
- [ ] Diagnosis output is deterministic for fixed inputs.
- [ ] Correlation views label association appropriately.

### Quality and engineering acceptance

- [ ] Required-field, duplicate, bounds, and state-consistency checks are covered by tests.
- [ ] Pipeline integration tests pass.
- [ ] Mart data quality tests pass.
- [ ] Performance benchmark tests pass within the documented target.
- [ ] No secrets or local runtime artifacts are required in version control.
- [ ] Documentation is updated when schemas or metric definitions change.

---

## 12. Error and Empty-State Requirements

| Condition | Required behavior |
|---|---|
| Database missing | Show a clear setup message instructing the user to run the ingestion pipeline |
| Raw input missing | Generate deterministic reference data or show a controlled ingestion error |
| Quality gate failed | Show failed checks and prevent unsupported interpretation |
| No anomalies | Show an informative empty state; do not render a dataframe error |
| Unknown city filter | Return an empty result safely and preserve page layout |
| Missing expected mart column | Fail with a clear contract error during development/testing, not a hidden page traceback |
| Slow query | Preserve page usability and expose latency where appropriate |

---

## 13. Release Scope

### Current release: Reference analytical product

Included:

- Deterministic synthetic data generator.
- CSV ingestion and transformation pipeline.
- Validation and quality reporting.
- DuckDB staging and analytical marts.
- KPI, correlation, anomaly, and deterministic diagnosis engines.
- Five-page Streamlit dashboard.
- Unit, integration, data-quality, and performance tests.
- Architecture, methodology, assumptions, security, and data dictionary documentation.

Not included:

- Production event-stream connectors.
- Hosted deployment and authentication.
- Alert delivery to email, chat, or incident-management systems.
- Forecasting, optimization, or recommended staffing quantities.
- Historical retention and multi-run comparison storage.

---

## 14. Roadmap

### Phase 1: Production data readiness

- Define production event contract and ownership.
- Add a production connector or object-storage ingestion path.
- Add schema versioning and run metadata.
- Add freshness, completeness, and late-arriving-event checks.
- Separate synthetic data configuration from production configuration.

### Phase 2: Operational workflow

- Add date-range and city filters shared across pages.
- Add exportable evidence summaries.
- Add alert delivery for critical recurring anomalies.
- Add run-to-run comparison and trend history.
- Add a documented intervention tracker outside the analytical mart.

### Phase 3: Governance and scale

- Add authentication and role-based access.
- Add managed analytical storage and scheduled refreshes.
- Add lineage and metric ownership metadata.
- Add privacy review and retention policies for production identifiers.
- Add observability for pipeline duration, query latency, and dashboard errors.

### Phase 4: Advanced decision support

- Add demand and capacity forecasting.
- Add scenario analysis for supply interventions.
- Add causal experiment measurement where operational interventions are randomized or controlled.
- Add market-level recommendation ranking with explicit confidence and evidence.

---

## 15. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Synthetic data does not represent production behavior | Decisions may not transfer to real operations | Validate generator distributions against production data before adoption |
| Correlation interpreted as causation | Incorrect operational intervention | Use explicit association language and require causal evidence for policy changes |
| P85 threshold shifts with data-window composition | Comparability changes between runs | Store threshold values and run metadata |
| Local DuckDB limits concurrent writes | Poor fit for multi-user production workloads | Keep DuckDB for local/reference use and move to managed analytical storage when needed |
| Marts drift from dashboard expectations | Runtime errors or incorrect displays | Add schema contract tests and versioned mart definitions |
| Missing or delayed events distort hourly rates | False anomaly signals | Add freshness, completeness, and late-data controls in production phase |
| Thresholds become stale | Misclassified market risk | Centralize settings and review thresholds against observed outcomes |

---

## 16. Open Questions

1. Which production systems own dispatch, acceptance, cancellation, pricing, and wait-time events?
2. What is the required data freshness for operations: hourly, fifteen-minute, or near real time?
3. Should risk thresholds be globally governed or configurable by market segment?
4. Which users may view city-level operational data, and what access restrictions are required?
5. What action-management system should receive critical anomaly alerts?
6. How should holidays, exceptional events, weather, and planned supply outages be represented?
7. What retention period and deletion policy apply to production event identifiers?
8. Should historical runs preserve changing P85 thresholds for longitudinal comparison?
9. What evidence is required before a diagnosis becomes an approved operational recommendation?

---

## 17. Traceability to Repository Artifacts

| Product area | Implementation/documentation |
|---|---|
| Configuration and thresholds | `src/config/settings.py` |
| Synthetic event generation | `src/ingestion/data_generator.py` |
| End-to-end ingestion | `src/ingestion/pipeline.py` |
| Cleaning and temporal features | `src/transformation/cleaner.py` |
| Validation | `src/validation/` |
| Database access | `src/database/` |
| KPI and diagnosis logic | `src/analytics/` |
| Staging schema | `sql/schema/staging.sql` |
| Analytical marts | `sql/marts/` |
| Dashboard shell and pages | `dashboard/` |
| Architecture and data flow | `docs/architecture.md` |
| Metric methodology | `docs/analytical_methodology.md` |
| Field definitions | `docs/data_dictionary.md` |
| Assumptions and thresholds | `docs/assumptions.md` |
| Security controls | `docs/security.md` |
| Automated tests | `tests/` |
