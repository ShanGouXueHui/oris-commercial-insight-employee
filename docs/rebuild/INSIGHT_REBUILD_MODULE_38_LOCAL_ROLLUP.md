# Insight Rebuild Module 38: Local Rollup

Date: 2026-06-26

## Status

accepted

## Acceptance Evidence

- Evidence commit: `5c518bf`
- Product base: `9d7d4edcf79aaa87081352068780a465d44c3d3a`
- Result: passed
- Expected test count: 211

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

## Verified Evidence

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_38_test_result.json`
- `reports/execution/insight_rebuild_module_38_execution_report.md`
