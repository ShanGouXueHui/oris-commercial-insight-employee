# Insight Rebuild Module 15 Test Plan

Date: 2026-06-24

## Module

Remote Runtime v2 Worker Queue Boundary

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 14 tests remain compatible.
3. Default queue adapter is disabled and local-runtime safe.
4. Disabled adapter enqueue does not dispatch remotely.
5. Remote boundary reports missing endpoint.
6. Remote boundary reports missing credential.
7. Remote boundary with endpoint and token is ready but not dispatched.
8. Dispatch-enabled flag is blocked until implementation exists.
9. Summary redacts credentials and reports no remote dispatch attempt.
10. Job ID generation is deterministic.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 15 status as `passed`.
- Evidence includes implementation files, tests, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 15 bootstrap entrypoint exists.
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
- Module 15 remote runtime queue tests: 8
- Expected total: 49
