# Insight Rebuild Module 7 Test Plan

Date: 2026-06-23

## Module

Runtime v2 Orchestration and Real Evidence Source Integration

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API surface remains compatible.
2. `/insights/rebuild/acceptance` reports Runtime v2 backed readiness.
3. `/insights/rebuild/brief` still returns accepted deterministic brief output for sample evidence.
4. Legacy `POST /insights/executive-brief` remains available.
5. Source/model/runtime settings are separated and default external providers to disabled.
6. Deterministic local source connector covers all required analytical lenses.
7. Runtime v2 orchestration adapter generates an accepted evidence-linked run.
8. Empty-evidence path remains repairable and does not falsely pass quality gates.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 7 status as `passed`.
- GitHub evidence includes implementation files, tests, test plan, execution report, and latest test result.
- No duplicate Module 7 bootstrap entrypoint exists.
- No `_v2`, `_v3`, `compat`, or `legacy` main entrypoint is introduced.

## Local Validation Result

The offline validation run completed successfully with 8 tests passing.
