# Insight Rebuild Module 11: Persistent Commercial Quota Ledger

Date: 2026-06-24

## Status

accepted

## Acceptance Evidence

- Local validation evidence commit: `8a8509ca7be4af26ecdb1c948436377c13322c1b`
- Evidence commit recorded in report: `132c11688076e4b7fcc7eccf09510e31f8faf258`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `25`

## Purpose

Module 11 turns the Module 10 in-memory commercial guardrail ledger into a configurable durable local ledger. This is needed before connecting live source providers or model providers, because quota and rate-limit state must survive process restarts in local smoke and pre-production environments.

## Implemented Scope

1. SQLite-backed guardrail usage ledger.
2. Ledger schema metadata table.
3. Per-client, per-minute usage counters.
4. Per-client, per-day usage counters.
5. Configurable ledger builder through environment variables.
6. Observability exposure for ledger storage mode and schema.
7. Health details exposure for persistent quota ledger readiness.
8. Unit tests for schema initialization, builder selection, persistence across instances, and summary output.
9. Official Module 11 bootstrap script.

## SQLite Schema

### `guardrail_metadata`

- `key TEXT PRIMARY KEY`
- `value TEXT NOT NULL`
- `updated_at TEXT NOT NULL`

Records:

- `schema_version = 2026-06-24-module-11`
- `ledger_type = sqlite`

### `guardrail_usage`

- `client_id TEXT NOT NULL`
- `scope TEXT NOT NULL`
- `bucket TEXT NOT NULL`
- `request_count INTEGER NOT NULL`
- `updated_at TEXT NOT NULL`
- primary key: `(client_id, scope, bucket)`

The `scope` value is either:

- `minute`
- `day`

## Environment Variables

```bash
ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE=in_memory
ORIS_INSIGHT_GUARDRAIL_LEDGER_PATH=reports/guardrails/guardrail_ledger.sqlite3
ORIS_INSIGHT_GUARDRAIL_LEDGER_SCHEMA_VERSION=2026-06-24-module-11
```

To enable the durable local ledger:

```bash
ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE=sqlite
```

## Default Behavior

Default ledger storage remains `in_memory` to preserve existing offline tests and local developer behavior.

SQLite is activated only when `ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE=sqlite` or an equivalent SQLite mode is configured.

## Observability

`GET /healthz/observability` now includes:

- `module_11_persistent_quota_ledger_ready=true`
- `guardrail_ledger.storage_mode`
- `guardrail_ledger.schema_version`
- `guardrail_ledger.tables`
- `guardrail_ledger.persistent_quota_ready`

`GET /healthz/details` now includes:

- `module_11_persistent_quota_ledger=true`

## Compatibility

Module 11 keeps Module 10 commercial guardrail policy unchanged:

- default observe mode remains non-blocking;
- blocking mode remains optional;
- health paths remain exempt;
- structured error behavior remains unchanged;
- response guardrail headers remain unchanged.

## Explicit Non-Scope

Module 11 does not add:

- distributed rate limiting;
- managed production database;
- tenant database schema;
- billing integration;
- OAuth/OIDC;
- live web/search connector;
- live model/provider connector;
- production deployment.

## Next Recommended Module After Acceptance

Module 12 should focus on one of:

1. authenticated source/model provider adapter behind the guardrail boundary;
2. managed production database transition plan;
3. remote ORIS Runtime v2 worker queue integration;
4. tenant and billing schema.
