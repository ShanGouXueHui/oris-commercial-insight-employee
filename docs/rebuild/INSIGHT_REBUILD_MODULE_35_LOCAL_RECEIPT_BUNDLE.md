# Insight Rebuild Module 35: Local Receipt Bundle

Date: 2026-06-26

## Status

implemented_pending_execution_evidence

## Purpose

Module 35 adds local receipt bundle summary visibility.

## Scope

- Bundle helper added at `app/local_manifest_receipt_bundle.py`.
- Tests added in `tests/test_module_35_local_receipt_bundle.py`.
- Runner added at `scripts/m35.sh`.
- Writer added at `scripts/w35.py`.

## Safety

- Disabled by default.
- Local bundle visibility only.
- No file export is written.
- Existing request behavior remains unchanged.

## Expected Test Count

199
