# Tenant Operational Audit Query Guide

Date: 2026-06-25

## Purpose

Module 29 adds a bounded read-only tenant operational audit query helper. It is designed for local operational visibility over audit events produced by Module 28.

## Default Behavior

The query boundary is disabled by default.

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED=false
```

When disabled, query helpers return a denied result with no events.

## Explicit Enablement

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED=true
```

## Query Behavior

The query helper supports:

- tenant-specific reads
- all-tenant local reads
- bounded result limits
- in-memory audit trail reads
- SQLite audit trail reads when a local SQLite trail is explicitly supplied or configured

## Safety Rules

- Disabled by default.
- Read-only.
- Explicit configuration required.
- Query result limit is bounded.
- No external storage service, billing provider, payment processor, provider call, remote runtime dispatch, or live external database connection is enabled.
