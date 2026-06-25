# Tenant Usage Admin API Guide

Date: 2026-06-25

## Purpose

Module 27 adds a bounded read-only tenant usage/admin visibility API. It exposes tenant usage records from the existing tenant usage ledger without changing default behavior.

## Default Behavior

The API is disabled by default.

```text
ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED=false
```

When disabled, the tenant usage admin endpoint returns a disabled response instead of exposing usage data.

## Explicit Enablement

To enable the read-only API, configure:

```text
ORIS_INSIGHT_TENANT_USAGE_ADMIN_API_ENABLED=true
ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS=<admin-key>
```

Optional settings:

| Setting | Default | Purpose |
| --- | --- | --- |
| `ORIS_INSIGHT_TENANT_USAGE_ADMIN_HEADER` | `x-oris-admin-key` | Header used for admin read access. |
| `ORIS_INSIGHT_TENANT_USAGE_ADMIN_KEYS` | empty | Comma-separated accepted admin keys. Values are masked in settings output. |
| `ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE` | `in_memory` | Set to `sqlite` to read from local durable SQLite storage. |
| `ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH` | `reports/tenant_usage/tenant_usage_ledger.sqlite3` | SQLite path when durable local storage is enabled. |

## Endpoint

```text
GET /insights/admin/tenant-usage?tenant_id=<tenant-id>&period=<YYYY-MM>
```

Required:

- `tenant_id`
- admin key header, default `x-oris-admin-key`

Optional:

- `period`; if omitted, current UTC monthly period is used.

## Response Boundary

The endpoint is read-only. It does not call `consume`, does not mutate usage, and does not connect to billing or payment systems.

## Safety Rules

- Disabled by default.
- Requires explicit admin API enablement.
- Requires an explicit admin key.
- Admin keys are never returned in settings or API payloads.
- Endpoint reads from in-memory or explicitly configured local SQLite tenant usage ledger.
- No external storage service, billing provider, payment processor, provider call, remote runtime dispatch, or live external database connection is enabled.
