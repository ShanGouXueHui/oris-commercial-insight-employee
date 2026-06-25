# Insight Rebuild Module 20 Test Plan

Date: 2026-06-25

## Module

Evidence Harness Helper

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 19 tests remain compatible.
3. Test run snapshot status comes from exit code.
4. Latest result payload contains required fields.
5. Sensitive values are redacted.
6. Execution report contains boundaries and pending SHA marker.
7. Harness writer writes latest result, module result, and report files.
8. Evidence commit SHA recorder replaces pending marker.
9. Summary reports reusable helper flags.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 20 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 20 bootstrap entrypoint exists.
- Module 20 bootstrap uses `app.evidence_harness` to write evidence.

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
- Module 15 remote runtime queue tests: 8
- Module 16 tenant entitlement tests: 7
- Module 17 reuse adoption tests: 7
- Module 18 loop engineering tests: 8
- Module 19 harness upgrade loop tests: 6
- Module 20 evidence harness tests: 7
- Expected total: 84
