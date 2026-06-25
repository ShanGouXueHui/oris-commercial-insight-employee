# Insight Rebuild Module 28 Test Plan

Date: 2026-06-25

## Module

Tenant Operational Audit Trail

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 1 through Module 27 tests remain compatible.
3. Operational audit trail is disabled by default.
4. In-memory audit trail records and lists events.
5. Default builder returns in-memory audit trail.
6. SQLite audit trail persists events across instances.
7. SQLite audit trail creates metadata and event rows.
8. Builder uses SQLite only when explicitly configured.
9. Summary reports enabled SQLite without external actions.
10. Health details reports Module 28 audit summary.
11. Official Module 28 bootstrap uses `app.evidence_harness` to write evidence.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 28 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 28 bootstrap entrypoint exists.
- Module 28 is not marked accepted until user-controlled evidence is pushed and verified.

## Expected Unit Test Count

The current full repository unittest discovery suite should run 168 tests after Module 28.

- Module 28 tenant operational audit tests added in this module: 8
- Expected full-suite total: 168
