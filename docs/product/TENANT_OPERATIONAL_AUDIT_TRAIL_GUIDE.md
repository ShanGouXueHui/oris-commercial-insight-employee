# Tenant Operational Audit Trail Guide

Date: 2026-06-25

## Purpose

Module 28 adds a bounded tenant operational audit event trail. It is intended for local operational observability of tenant usage visibility actions.

## Default Behavior

The audit trail is disabled by default.

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_ENABLED=false
```

When disabled, no operational audit events are recorded and existing request behavior remains unchanged.

## Explicit Enablement

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_ENABLED=true
```

Optional local durable storage:

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_STORAGE=sqlite
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_PATH=reports/tenant_usage/tenant_operational_audit.sqlite3
```

## Supported Storage Modes

- `in_memory`, default local deterministic mode.
- `sqlite`, optional local durable mode.

## Event Shape

Each event records:

- `event_id`
- `event_type`
- `actor_id`
- `tenant_id`
- `period`
- `operation`
- `result`
- `created_at`
- `audit_version`

## Safety Rules

- Disabled by default.
- Explicit configuration required.
- Local deterministic storage by default.
- Optional SQLite is local durable storage only.
- No external storage service, billing provider, payment processor, provider call, remote runtime dispatch, or live external database connection is enabled.
- Gate values are not stored in audit events.
