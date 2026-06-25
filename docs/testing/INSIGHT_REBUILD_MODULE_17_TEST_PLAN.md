# Insight Rebuild Module 17 Test Plan

Date: 2026-06-25

## Module

Reusable Skills and Harness Adoption Boundary

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 16 tests remain compatible.
3. High-quality reusable candidate is adopted.
4. Unapproved license is rejected.
5. Network and secret requirements prevent direct adoption.
6. Default candidates include harness and AGENTS.md options.
7. Adoption plan disables custom-code default.
8. Summary reports reuse boundary counts.
9. Scoring penalizes network and secret requirements.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 17 status as `passed`.
- Evidence includes implementation files, tests, AGENTS.md, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 17 bootstrap entrypoint exists.

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
- Expected total: 63
