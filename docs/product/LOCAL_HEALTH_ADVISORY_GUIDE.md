# Local Health Advisory Guide

Date: 2026-06-26

## Purpose

Module 37 adds local advisory visibility for receipt bundle health status.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_HEALTH_ADVISORY_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_HEALTH_ADVISORY_ENABLED=true
```

## Rules

- Local advisory visibility only.
- Advisory is derived from health status.
- No export file is written.
- No external action is executed.
- Existing request behavior is unchanged.
