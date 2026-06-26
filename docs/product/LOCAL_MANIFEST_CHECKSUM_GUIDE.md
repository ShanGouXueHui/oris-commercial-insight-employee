# Local Manifest Checksum Guide

Date: 2026-06-26

## Purpose

Module 32 adds a local checksum helper for local manifests.

## Default

Disabled by default.

```text
ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED=true
```

## Rules

- Local checksum visibility only.
- SHA-256 checksum.
- No export file is written.
- Existing request behavior is unchanged.
