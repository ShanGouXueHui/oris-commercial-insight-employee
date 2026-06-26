# Local Receipt Bundle Health Guide

Date: 2026-06-26

## Purpose

Module 36 adds local receipt bundle health summary visibility.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_HEALTH_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_HEALTH_ENABLED=true
```

## Rules

- Local health visibility only.
- Health states include empty, healthy, partial, and attention required.
- No export file is written.
- Existing request behavior is unchanged.
