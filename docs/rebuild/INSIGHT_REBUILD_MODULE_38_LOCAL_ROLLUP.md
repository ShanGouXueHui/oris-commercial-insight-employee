# Insight Rebuild Module 38: Local Rollup

Date: 2026-06-26

## Status

implemented_pending_execution_evidence

## Purpose

Module 38 adds local rollup visibility.

## Scope

- Helper added at `app/m38.py`.
- Tests added in `tests/test_module_38_m38.py`.
- Runner added at `scripts/r38.sh`.
- Writer added at `scripts/w38.py`.

## Safety

- Disabled by default.
- Local rollup visibility only.
- No file export is written.
- Existing request behavior remains unchanged.

## Expected Test Count

211
