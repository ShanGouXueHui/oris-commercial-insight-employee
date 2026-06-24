# Insight Rebuild Module 10 Test Plan

Date: 2026-06-24

## Module

Commercial Guardrails

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API surface remains compatible.
2. Existing Module 7 orchestration tests remain compatible.
3. Existing Module 8 durable persistence tests remain compatible.
4. Existing Module 9 observability tests remain compatible.
5. Default guardrail mode is observe/non-blocking.
6. Rebuild acceptance reports commercial guardrail readiness.
7. Blocking mode rejects commercial endpoints when required API key is missing.
8. Blocking mode allows requests with a configured valid API key.
9. Per-minute rate limit can block excess requests with HTTP 429.
10. Health endpoints remain exempt in blocking mode.
11. Blocked requests return structured JSON error payloads.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 10 status as `passed`.
- GitHub evidence includes implementation files, tests, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 10 bootstrap entrypoint exists.
- No `_v2`, `_v3`, `compat`, or `legacy` main entrypoint is introduced.

## Expected Unit Test Count

- Module 6 API surface tests: 4
- Module 7 orchestration tests: 4
- Module 8 durable persistence tests: 4
- Module 9 observability tests: 4
- Module 10 commercial guardrail tests: 5
- Expected total: 21

## Non-Scope Checks

Module 10 should not require:

- live web/search access;
- external model/provider access;
- production managed database;
- production deployment;
- OAuth/OIDC integration;
- persistent quota ledger.
