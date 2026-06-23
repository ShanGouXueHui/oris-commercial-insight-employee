# Insight Rebuild Module 6 - API Surface and Acceptance

## Objective

Expose the Runtime v2 backed rebuild pipeline through the FastAPI application while keeping the legacy Phase 0 endpoint available.

## API Surface

- `GET /healthz/details` reports version `0.2.0` and `runtime_v2_backed_rebuild=true`.
- `GET /insights/rebuild/acceptance` reports rebuild readiness.
- `POST /insights/rebuild/brief` generates a deterministic evidence-linked brief with quality assessment.
- `POST /insights/executive-brief` remains available for backward compatibility.

## Acceptance Scope

Module 6 verifies the API surface through FastAPI TestClient tests. It does not add external evidence sources or production deployment.

## Next Module

Insight Rebuild Module 7: Runtime v2 Orchestration and Real Evidence Source Integration.
