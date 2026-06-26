# Insight Rebuild Module 36: Local Receipt Bundle Health

Date: 2026-06-26

## Status

implemented_pending_execution_evidence

## Purpose

Module 36 adds local receipt bundle health summary visibility.

## Scope

- Health helper added at `app/local_receipt_bundle_health.py`.
- Tests added in `tests/test_module_36_local_receipt_bundle_health.py`.
- Runner added at `scripts/m36.sh`.
- Writer added at `scripts/w36.py`.

## Safety

- Disabled by default.
- Local health visibility only.
- No file export is written.
- Existing request behavior remains unchanged.

## Expected Test Count

203
