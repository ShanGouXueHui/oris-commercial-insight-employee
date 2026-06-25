# Durable Tenant Usage Ledger Guide

Date: 2026-06-25

## Purpose

Module 26 adds an optional durable local tenant usage ledger backed by SQLite. It extends the Module 24 in-memory tenant usage ledger and the Module 25 tenant middleware bridge without changing default behavior.

## Default Behavior

The default tenant usage ledger remains in-memory.

```text
ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE=in_memory
```

No SQLite file is created unless durable local storage is explicitly configured.

## Explicit Durable Storage Configuration

| Setting | Default | Purpose |
| --- | --- | --- |
| `ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE` | `in_memory` | Set to `sqlite` to use local durable SQLite storage. |
| `ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH` | `reports/tenant_usage/tenant_usage_ledger.sqlite3` | Local SQLite file path. |
| `ORIS_INSIGHT_TENANT_USAGE_LEDGER_SCHEMA_VERSION` | `2026-06-25-module-26` | Durable tenant usage schema version marker. |

Supported explicit durable storage modes:

- `sqlite`
- `sqlite_durable`
- `durable_sqlite`

## SQLite Tables

Module 26 creates two local tables when SQLite mode is explicitly configured:

- `tenant_usage_metadata`
- `tenant_usage`

`tenant_usage` stores request counts by `(tenant_id, period)`.

## Middleware Integration

The middleware uses the configured tenant usage ledger only when tenant usage ledger behavior is explicitly enabled:

```text
ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED=true
ORIS_INSIGHT_TENANT_USAGE_LEDGER_ENABLED=true
ORIS_INSIGHT_TENANT_USAGE_CONSUME_ON_ALLOWED_REQUEST=true
ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE=sqlite
```

If these flags are not set, existing default behavior remains unchanged.

## Safety Rules

- SQLite is local durable storage, not a managed database service.
- No live external database connection is enabled.
- No billing provider is integrated.
- No payment processing is enabled.
- No provider call or remote runtime dispatch is enabled.
- The in-memory ledger remains the deterministic default.
