# Insight Rebuild Module 13 Test Plan

Date: 2026-06-24

## Module

Managed Database Transition Plan

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 12 tests remain compatible.
3. Manifest contains evidence persistence tables.
4. Manifest contains guardrail ledger tables.
5. PostgreSQL manifest is boundary-only.
6. CREATE TABLE rendering includes primary key definitions.
7. Migration order matches table order.
8. Transition summary reports no live connection and no production cutover.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 13 status as `passed`.
- Evidence includes implementation files, tests, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 13 bootstrap entrypoint exists.
- No duplicate `_v2`, `_v3`, `compat`, or `legacy` main entrypoint is introduced.

## Expected Unit Test Count

- Module 6 API surface tests: 4
- Module 7 orchestration tests: 4
- Module 8 durable persistence tests: 4
- Module 9 observability tests: 4
- Module 10 commercial guardrail tests: 5
- Module 11 persistent ledger tests: 4
- Module 12 provider adapter tests: 5
- Module 13 managed database transition tests: 5
- Expected total: 35
