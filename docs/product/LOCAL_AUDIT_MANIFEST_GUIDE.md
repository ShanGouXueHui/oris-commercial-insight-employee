# Local Audit Manifest Guide

Date: 2026-06-25

## Purpose

Module 31 adds a local manifest helper for operational audit summaries.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_AUDIT_MANIFEST_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_AUDIT_MANIFEST_ENABLED=true
```

## Rules

- Manifest-only.
- Local configuration only.
- Count is bounded to 1000.
- Existing request behavior is unchanged.
