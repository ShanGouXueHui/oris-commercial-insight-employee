# Local Rollup Health Guide

Date: 2026-06-26

## Purpose

Module 39 adds local health visibility for rollup output.

## Default

Disabled by default.

```text
ORIS_INSIGHT_M39_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_M39_ENABLED=true
```

## Rules

- Local visibility only.
- Health states include empty, ready, and bounded.
- No export file is written.
- Existing request behavior is unchanged.
