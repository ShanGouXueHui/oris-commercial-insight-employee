# Insight Rebuild Module 26 Test Plan

Date: 2026-06-25

## Module

Durable Tenant Usage Ledger

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 1 through Module 25 tests remain compatible.
3. Default tenant usage storage remains `in_memory`.
4. SQLite tenant usage ledger persists counts across ledger instances.
5. SQLite tenant usage ledger creates metadata and usage rows.
6. Ledger builder uses SQLite only when explicitly configured.
7. Summary reports SQLite durable storage without external storage or live external actions.
8. Middleware uses configured SQLite tenant usage ledger when tenant usage flags and storage mode are explicitly enabled.
9. Health details reports durable tenant usage storage configuration.
10. Official Module 26 bootstrap uses `app.evidence_harness` to write evidence.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 26 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 26 bootstrap entrypoint exists.
- Module 26 is not marked accepted until user-controlled evidence is pushed and verified.

## Expected Unit Test Count

The current full repository unittest discovery suite should run 151 tests after Module 26.

- Module 26 durable tenant usage ledger tests added in this module: 7
- Expected full-suite total: 151
