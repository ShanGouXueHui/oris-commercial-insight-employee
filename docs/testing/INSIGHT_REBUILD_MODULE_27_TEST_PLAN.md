# Insight Rebuild Module 27 Test Plan

Date: 2026-06-25

## Module

Tenant Usage Admin API

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 1 through Module 26 tests remain compatible.
3. Tenant usage admin API is disabled by default.
4. Enabled tenant usage admin API requires configured admin access value.
5. Invalid admin access value is rejected and sensitive values are not echoed.
6. Admin access values are masked in settings payloads.
7. Admin API reads in-memory tenant usage when explicitly enabled.
8. Admin API reads SQLite tenant usage when explicitly configured.
9. Admin API read does not consume usage even when tenant middleware consumption is enabled.
10. Health details reports Module 27 admin API summary.
11. Access evaluator allows only enabled policy with matching admin access value.
12. Official Module 27 bootstrap uses `app.evidence_harness` to write evidence.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 27 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 27 bootstrap entrypoint exists.
- Module 27 is not marked accepted until user-controlled evidence is pushed and verified.

## Expected Unit Test Count

The current full repository unittest discovery suite should run 160 tests after Module 27.

- Module 27 tenant usage admin API tests added in this module: 9
- Expected full-suite total: 160
