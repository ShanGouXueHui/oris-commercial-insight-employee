# Insight Rebuild Module 9 Test Plan

Date: 2026-06-24

## Module

Deployment Smoke Test and Runtime Observability

## Unit Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Smoke Command

The official bootstrap script starts uvicorn and runs:

`python3 scripts/run_module_9_smoke.py`

## Required Unit Coverage

1. Existing API surface remains compatible.
2. Existing Module 7 orchestration tests remain compatible.
3. Existing Module 8 durable persistence tests remain compatible.
4. Observability snapshot reports healthy status.
5. `/healthz/observability` returns smoke readiness.
6. `/healthz/details` includes observability payload.
7. `/insights/rebuild/acceptance` reports Module 9 smoke readiness.

## Required Smoke Coverage

1. A real uvicorn process starts locally.
2. `GET /healthz` returns healthy.
3. `GET /healthz/details` returns Runtime v2 and Module 9 observability status.
4. `GET /healthz/observability` returns smoke readiness.
5. `GET /insights/rebuild/acceptance` reports Module 9 smoke readiness.
6. `POST /insights/rebuild/brief` returns an accepted brief.
7. The brief response reports `evidence_persistence.storage_mode=sqlite`.
8. SQLite contains at least one runtime run and at least one evidence item after the smoke run.

## Acceptance Criteria

- Unit test exit code is `0`.
- Smoke test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 9 status as `passed`.
- `reports/testing/insight_rebuild_module_9_smoke_result.json` records endpoint and SQLite checks.
- GitHub evidence includes implementation files, tests, test plan, execution report, smoke result, latest test result, and bootstrap log.
- Exactly one official Module 9 bootstrap entrypoint exists.
- No `_v2`, `_v3`, `compat`, or `legacy` main entrypoint is introduced.

## Expected Unit Test Count

- Module 6 API surface tests: 4
- Module 7 orchestration tests: 4
- Module 8 durable persistence tests: 4
- Module 9 observability tests: 4
- Expected total: 16
