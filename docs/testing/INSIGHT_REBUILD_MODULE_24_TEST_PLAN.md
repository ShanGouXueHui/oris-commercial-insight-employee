# Insight Rebuild Module 24 Test Plan

Date: 2026-06-25

## Module

Tenant Usage Ledger

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 23 tests remain compatible.
3. Monthly period helper is deterministic.
4. Empty ledger returns zero usage.
5. Consume increments monthly usage.
6. Snapshot reports current count.
7. Entitlement evaluation uses ledger usage under quota.
8. Entitlement evaluation blocks at quota.
9. Summary reports local-only ledger flags.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 24 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 24 bootstrap entrypoint exists.
- Module 24 bootstrap uses `app.evidence_harness` to write evidence.

## Expected Unit Test Count

The current full repository unittest discovery suite should run 137 tests after Module 24.

- Module 24 tenant usage ledger tests added in this module: 7
- Expected full-suite total: 137
