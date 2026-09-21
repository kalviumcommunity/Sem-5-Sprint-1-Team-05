# Security Controls & Governance — Ride-Sharing Ops Platform

## 1. Secrets & Configuration Security
- **No Hardcoded Credentials:** All environmental parameters are loaded dynamically via `pydantic-settings` from `.env`.
- **Committed Example:** `.env.example` is checked into version control; `.env` is explicitly ignored in `.gitignore`.

## 2. Input Validation & SQL Injection Prevention
- **Parameterized SQL Execution:** All analytical query functions use positional parameters (`?`) rather than string interpolation or format strings.
- **Pydantic Validation:** Ingestion boundaries strictly enforce field bounds, ranges ($1.0 \le \text{surge} \le 10.0$), and data types.

## 3. Data Minimization & Privacy (PII Protection)
- **Driver & Rider Identifiers:** No personal names, telephone numbers, or payment tokens are stored in the analytical marts. Dispatched IDs are anonymized surrogate tokens (`DRV-XXXX`, `REQ-XXXX`).

## 4. Container & Runtime Security
- **Non-Root Execution:** The production Dockerfile creates and executes under a restricted `appuser` (UID 1000).
- **Minimal Image Surface:** Built using Python 3.11 Slim with multi-stage build eliminating development toolchains from the final image.
