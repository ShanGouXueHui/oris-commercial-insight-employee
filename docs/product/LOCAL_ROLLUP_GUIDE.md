# Local Rollup Guide

Date: 2026-06-26

## Purpose

Module 38 adds local rollup visibility.

## Default

Disabled by default.

```text
ORIS_INSIGHT_M38_ENABLED=false
```

## Enablement

```text
ORIS_INSIGHT_M38_ENABLED=true
```

## Rules

- Local visibility only.
- Rollup size is bounded to 100 items.
- No export file is written.
- Existing request behavior is unchanged.
