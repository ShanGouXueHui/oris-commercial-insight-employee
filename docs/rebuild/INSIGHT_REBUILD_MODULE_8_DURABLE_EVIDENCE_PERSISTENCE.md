# Insight Rebuild Module 8: Durable Evidence Persistence and Database Schema

Date: 2026-06-24

## Status

accepted

## Purpose

Module 8 hardens the Module 7 evidence persistence boundary into a durable, dependency-free database-backed store. The goal is not to introduce production infrastructure yet. The goal is to establish a concrete schema and adapter path so future deployment smoke tests, real source connectors, and model/provider integrations can write auditable evidence records.

## Implemented Scope

1. Durable SQLite evidence store.
2. Evidence persistence schema versioning.
3. Runtime run table.
4. Evidence source table.
5. Evidence item table.
6. Persistence metadata table.
7. Config-driven storage mode selection.
8. Runtime adapter compatibility with SQLite persistence.
9. API readiness exposure for durable persistence.
10. Unit tests and GitHub evidence.

## Schema

Module 8 introduces `SQLiteEvidenceStore` in `app/evidence_persistence.py`.

Schema version:

`2026-06-24-module-8`

Tables:

1. `persistence_metadata`
   - key/value metadata for schema version and store type.

2. `runtime_runs`
   - one row per Runtime v2 product run.
   - records runtime run ID, subject company, storage mode, persisted timestamp, schema version, source count, evidence count, and validation error count.

3. `evidence_sources`
   - normalized evidence source records per runtime run.
   - records source ID, source type, title, credibility score, and URL.

4. `evidence_items`
   - normalized evidence item records per runtime run.
   - records evidence ID, source ID, analytical lens, claim text, and relevance score.

## Configuration

`EvidencePersistenceSettings` now includes:

- `storage_mode`
- `local_path`
- `persist_full_claim_text`
- `schema_version`

Supported storage modes:

- `in_memory` default;
- `filesystem` development option from Module 7;
- `sqlite` durable option from Module 8.

Environment configuration:

```bash
ORIS_INSIGHT_EVIDENCE_STORAGE=sqlite
ORIS_INSIGHT_EVIDENCE_LOCAL_PATH=reports/evidence/runtime_runs/insight.sqlite3
```

Default behavior remains `in_memory` so existing deterministic API tests remain stable.

## Runtime Integration

`LocalRuntimeV2OrchestrationAdapter` already receives its evidence store through `build_evidence_store(settings.evidence_persistence)`. Module 8 extends that factory to return `SQLiteEvidenceStore` when `storage_mode=sqlite`.

The Runtime v2 run path remains:

1. Build domain contract.
2. Fetch evidence through the source connector.
3. Ingest evidence.
4. Generate brief.
5. Run quality gates.
6. Persist evidence through the configured store.
7. Return Runtime v2 aligned payload.

## API Integration

`GET /insights/rebuild/acceptance` now reports:

- `module_8_durable_persistence=true`
- `durable_evidence_store=sqlite_available`
- `evidence_persistence` settings
- `evidence_schema` summary

`POST /insights/rebuild/brief` continues to return `evidence_persistence` in the response payload. When SQLite is enabled by environment, the persistence record reports `storage_mode=sqlite` and the configured database path.

## Explicit Non-Scope

Module 8 does not add:

- production managed database;
- cache layer;
- tenant isolation;
- auth/quota/rate limiting;
- live web/search/provider ingestion;
- deployment smoke test.

## Next Recommended Module

Module 9 should focus on deployment smoke testing and runtime observability, or on authenticated external source/provider adapters using the config and approval boundaries established by Modules 7 and 8.
