# Insight Rebuild Module 36: Local Receipt Bundle Health

Date: 2026-06-26

## Status

accepted

## Acceptance Evidence

- Evidence commit: `c2372c9`
- Product base: `1c4c10075ee2ef68d1432f919361cab3ab63f7db`
- Result: passed
- Expected test count: 203

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

## Verified Evidence

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_36_test_result.json`
- `reports/execution/insight_rebuild_module_36_execution_report.md`
