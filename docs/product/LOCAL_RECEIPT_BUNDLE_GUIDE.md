# Local Receipt Bundle Guide

Date: 2026-06-26

## Purpose

Module 35 adds local receipt bundle summary visibility.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_ENABLED=true
```

## Rules

- Local bundle visibility only.
- Bundle size is bounded to 100 receipts.
- No export file is written.
- Existing request behavior is unchanged.
