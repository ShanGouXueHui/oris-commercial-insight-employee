# Insight Rebuild Module 11 Test Plan

Date: 2026-06-24

## Module

Persistent Commercial Quota Ledger

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7, 8, 9, and 10 tests remain compatible.
3. SQLite guardrail ledger initializes required tables.
4. Ledger builder selects SQLite when configured.
5. SQLite usage counters persist across ledger instances.
6. Ledger summary reports SQLite mode, schema, and tables.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 11 status as `passed`.
- Evidence includes implementation files, tests, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 11 bootstrap entrypoint exists.
- No duplicate `_v2`, `_v3`, `compat`, or `legacy` main entrypoint is introduced.

## Expected Unit Test Count

- Module 6 API surface tests: 4
- Module 7 orchestration tests: 4
- Module 8 durable persistence tests: 4
- Module 9 observability tests: 4
- Module 10 commercial guardrail tests: 5
- Module 11 persistent ledger tests: 4
- Expected total: 25
