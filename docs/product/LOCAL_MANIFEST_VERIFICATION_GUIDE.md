# Local Manifest Verification Guide

Date: 2026-06-26

## Purpose

Module 33 adds a local verification helper for manifest checksum status.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_MANIFEST_VERIFICATION_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_MANIFEST_VERIFICATION_ENABLED=true
```

## Rules

- Local verification visibility only.
- SHA-256 checksum comparison.
- No export file is written.
- Existing request behavior is unchanged.
