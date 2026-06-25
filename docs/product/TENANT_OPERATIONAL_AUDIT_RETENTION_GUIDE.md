# Tenant Operational Audit Retention Guide

Date: 2026-06-25

## Purpose

Module 30 adds a local visibility-only retention policy helper for operational audit records.

## Default

Disabled by default.

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_RETENTION_ENABLED=false
```

## Optional Local Settings

```text
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_RETENTION_ENABLED=true
ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_RETENTION_DAYS=180
```

## Rules

- Visibility-only.
- Local configuration only.
- Day values are bounded between 1 and 3650.
- Invalid values fall back to 90.
- Existing request behavior is unchanged.
