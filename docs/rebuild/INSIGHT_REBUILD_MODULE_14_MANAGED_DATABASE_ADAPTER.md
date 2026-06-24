# Insight Rebuild Module 14: Managed Database Adapter Boundary

Date: 2026-06-24

## Status

prepared_pending_local_unit_validation

## Purpose

Module 14 adds a managed database adapter boundary behind the Module 13 schema manifest. It prepares the runtime integration seam for a future managed PostgreSQL database while keeping the current SQLite runtime path active by default.

## Implemented Scope

1. Managed database adapter settings.
2. Disabled/default adapter for SQLite runtime safety.
3. PostgreSQL boundary adapter.
4. Migration preview using the Module 13 manifest.
5. Adapter readiness summary.
6. Credential presence detection without credential exposure.
7. Unit tests for default safety, missing credential, credential redaction, preview-only migration, and no live connection attempt.
8. Official Module 14 bootstrap script.

## Adapter Modes

### `disabled`

Default mode. SQLite/local runtime remains active. No managed database connection is attempted.

### `postgres_boundary`

Boundary mode for future PostgreSQL activation. It can detect whether a database credential is configured, but it does not connect to the database in Module 14.

## Environment Variables

```bash
ORIS_INSIGHT_MANAGED_DB_MODE=disabled
ORIS_INSIGHT_MANAGED_DB_TARGET=postgresql
ORIS_INSIGHT_MANAGED_DB_LIVE_CONNECTION_ENABLED=false
ORIS_INSIGHT_DATABASE_URL=<configured only in private runtime>
ORIS_INSIGHT_MANAGED_DB_DSN=<alternative private runtime DSN>
```

## Safety Properties

- Default behavior remains SQLite/local.
- Credentials are detected only as configured/not configured.
- Credentials are never returned in summaries.
- No live connection is attempted in Module 14.
- Migration preview is manifest-only.
- Production cutover remains out of scope.

## Explicit Non-Scope

Module 14 does not add:

- live managed database connection;
- production cutover;
- data backfill execution;
- connection pooling;
- runtime writes to PostgreSQL;
- tenant billing schema;
- secret manager integration.

## Acceptance Rule

Module 14 is accepted only after the official bootstrap script runs in the user-controlled local/server environment and pushes unit-test evidence to GitHub.

## Next Recommended Module After Acceptance

Module 15 should focus on one of:

1. remote Runtime v2 worker queue integration;
2. tenant and billing schema;
3. managed database live smoke in a controlled non-production environment;
4. provider-backed generation smoke with explicitly configured safe credentials.
