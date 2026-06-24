# Insight Rebuild Module 13: Managed Database Transition Plan

Date: 2026-06-24

## Status

prepared_pending_local_unit_validation

## Purpose

Module 13 defines a managed database transition boundary for the durable local SQLite data created by earlier modules. It prepares a PostgreSQL-compatible schema manifest without opening a live database connection or changing the default runtime store.

## Implemented Scope

1. Managed database table contract model.
2. PostgreSQL-compatible schema manifest.
3. Evidence persistence table coverage from Module 8.
4. Guardrail ledger table coverage from Module 11.
5. CREATE TABLE statement rendering.
6. Migration order manifest.
7. Managed database transition summary.
8. Unit tests for schema coverage, manifest safety, SQL rendering, migration order, and cutover flags.
9. Official Module 13 bootstrap script.

## Tables Covered

Evidence persistence tables:

- `persistence_metadata`
- `runtime_runs`
- `evidence_sources`
- `evidence_items`

Guardrail ledger tables:

- `guardrail_metadata`
- `guardrail_usage`

## Default Behavior

Runtime storage remains SQLite/local until a future module explicitly enables a managed database adapter. Module 13 only prepares the migration plan and schema manifest.

## Safety Properties

- No live database connection is opened.
- No production cutover is performed.
- No data backfill is executed.
- SQLite behavior remains unchanged.
- Provider and source connector behavior remains unchanged.

## Explicit Non-Scope

Module 13 does not add:

- live managed database connection;
- production database credentials;
- data backfill execution;
- production cutover;
- connection pooling;
- ORM migration framework;
- tenant billing schema.

## Acceptance Rule

Module 13 is accepted only after the official bootstrap script runs in the user-controlled local/server environment and pushes unit-test evidence to GitHub.

## Next Recommended Module After Acceptance

Module 14 should focus on one of:

1. managed database adapter implementation behind the Module 13 manifest;
2. remote Runtime v2 worker queue integration;
3. tenant and billing schema;
4. provider-backed generation smoke with explicitly configured safe credentials.
