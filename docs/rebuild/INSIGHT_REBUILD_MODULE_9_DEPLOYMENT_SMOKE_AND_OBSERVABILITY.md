# Insight Rebuild Module 9: Deployment Smoke Test and Runtime Observability

Date: 2026-06-24

## Status

prepared_pending_local_smoke_execution

## Purpose

Module 9 adds a deployment-smoke and runtime-observability boundary on top of the Module 7 orchestration adapter and Module 8 SQLite evidence persistence. This module is intentionally local/deployment-smoke oriented. It does not introduce production deployment automation, managed databases, live web/search providers, or external model providers.

## Implemented Scope

1. Runtime observability snapshot.
2. `/healthz/observability` endpoint.
3. Enhanced `/healthz/details` runtime observability payload.
4. Enhanced `/insights/rebuild/acceptance` smoke-readiness payload.
5. Local HTTP smoke runner for a real uvicorn process.
6. SQLite persistence verification during smoke run.
7. Unit tests for observability readiness.
8. Official Module 9 bootstrap script to run tests, start uvicorn, call endpoints, verify SQLite persistence, and push evidence.

## Observability Boundary

`app/observability.py` introduces:

- `RuntimeObservationCheck`
- `RuntimeObservabilitySnapshot`
- `build_runtime_observability_snapshot()`

The snapshot includes:

- generated timestamp;
- service start timestamp;
- service uptime seconds;
- API version;
- Runtime v2 backed status;
- Module 9 smoke readiness;
- source/model/provider guardrail checks;
- evidence schema summary;
- connector mode summary;
- full settings snapshot.

## API Changes

### `GET /healthz/details`

Now includes:

- `module_9_observability=true`
- `dependencies.sqlite3=ok`
- `observability` snapshot

### `GET /healthz/observability`

Returns the runtime observability snapshot directly.

### `GET /insights/rebuild/acceptance`

Now includes:

- `module_9_deployment_smoke_ready=true`
- `observability_boundary=true`
- `observability` snapshot

## Smoke Runner

`script/run_module_9_smoke.py` validates a real running service through HTTP:

1. `GET /healthz`
2. `GET /healthz/details`
3. `GET /healthz/observability`
4. `GET /insights/rebuild/acceptance`
5. `POST /insights/rebuild/brief`
6. SQLite row counts for runtime runs, evidence sources, and evidence items

The smoke runner writes:

- `reports/testing/insight_rebuild_module_9_smoke_result.json`

## Official Bootstrap

`script/bootstrap_insight_rebuild_module_9.sh` is the only official Module 9 executable entrypoint.

It performs:

1. Git fast-forward to main.
2. Duplicate Module 9 bootstrap guard.
3. Unit tests.
4. Start uvicorn on `127.0.0.1:8099`.
5. Set SQLite evidence persistence env.
6. Run Module 9 smoke runner.
7. Stop uvicorn.
8. Write `reports/testing/latest_test_result.json`.
9. Write `reports/execution/insight_rebuild_module_9_execution_report.md`.
10. Commit and push evidence.

## Explicit Non-Scope

Module 9 does not add:

- production deployment;
- managed production database;
- cache layer;
- auth, tenant, quota, or rate-limit guardrails;
- live web/search source connector;
- external model/provider connector.

## Acceptance Rule

Module 9 is not accepted from GitHub-side preparation alone. It becomes accepted only after the official bootstrap script runs in the user-controlled local/server environment and pushes smoke evidence to GitHub.

## Next Recommended Module After Acceptance

Module 10 should focus on one of:

1. authenticated source/model provider adapter;
2. commercial guardrails such as auth/quota/rate limits;
3. managed database transition plan from SQLite schema to PostgreSQL or equivalent.
