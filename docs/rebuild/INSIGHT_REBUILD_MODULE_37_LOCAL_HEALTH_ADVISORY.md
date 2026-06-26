# Insight Rebuild Module 37: Local Health Advisory

Date: 2026-06-26

## Status

implemented_pending_execution_evidence

## Purpose

Module 37 adds local health advisory visibility.

## Scope

- Advisory helper added at `app/local_health_advisory.py`.
- Tests added in `tests/test_module_37_local_health_advisory.py`.
- Runner added at `scripts/m37.sh`.
- Writer added at `scripts/w37.py`.

## Safety

- Disabled by default.
- Local advisory visibility only.
- No file export is written.
- No external action is executed.
- Existing request behavior remains unchanged.

## Expected Test Count

207
