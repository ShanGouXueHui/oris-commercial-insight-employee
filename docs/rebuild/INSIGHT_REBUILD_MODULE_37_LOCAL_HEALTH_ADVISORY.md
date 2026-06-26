# Insight Rebuild Module 37: Local Health Advisory

Date: 2026-06-26

## Status

accepted

## Acceptance Evidence

- Evidence commit: `07471ef`
- Product base: `aad46c38df8dae5c111b4e3664929e2f938a408f`
- Result: passed
- Expected test count: 207

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

## Verified Evidence

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_37_test_result.json`
- `reports/execution/insight_rebuild_module_37_execution_report.md`
