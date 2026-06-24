# Insight Rebuild Module 14 Test Plan

Date: 2026-06-24

## Module

Managed Database Adapter Boundary

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 13 tests remain compatible.
3. Default adapter remains disabled and SQLite-runtime safe.
4. PostgreSQL boundary reports missing credential.
5. PostgreSQL boundary detects credential without exposing secret.
6. Migration preview is manifest-only.
7. Summary reports no live connection attempt.
8. Live connection flag can be read without attempting a connection.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 14 status as `passed`.
- Evidence includes implementation files, tests, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 14 bootstrap entrypoint exists.
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
- Module 14 managed database adapter tests: 6
- Expected total: 41
