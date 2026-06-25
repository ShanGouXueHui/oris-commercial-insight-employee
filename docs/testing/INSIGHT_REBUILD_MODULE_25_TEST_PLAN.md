# Insight Rebuild Module 25 Test Plan

Date: 2026-06-25

## Module

Tenant Middleware Usage Ledger Bridge

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 1 through Module 24 tests remain compatible.
3. Default tenant usage ledger middleware flags are disabled.
4. Disabled default path does not emit tenant usage headers.
5. Explicit configuration enables the usage ledger bridge summary.
6. Ledger usage blocks a tenant at monthly quota.
7. Allowed requests consume tenant usage only when explicitly enabled.
8. Middleware emits tenant usage headers when explicit flags are enabled.
9. Exempt paths do not consume tenant usage.
10. Official Module 25 bootstrap uses `app.evidence_harness` to write evidence.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 25 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 25 bootstrap entrypoint exists.
- Module 25 is not marked accepted until user-controlled evidence is pushed and verified.

## Expected Unit Test Count

The current full repository unittest discovery suite should run 144 tests after Module 25.

- Module 25 tenant middleware usage ledger tests added in this module: 7
- Expected full-suite total: 144
