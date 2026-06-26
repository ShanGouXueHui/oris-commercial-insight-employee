# Local Manifest Receipt Guide

Date: 2026-06-26

## Purpose

Module 34 adds a local receipt helper for manifest integrity status.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_MANIFEST_RECEIPT_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_MANIFEST_RECEIPT_ENABLED=true
```

## Rules

- Local receipt visibility only.
- Receipt can include checksum and optional verification result.
- No export file is written.
- Existing request behavior is unchanged.
