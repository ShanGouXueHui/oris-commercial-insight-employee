# Insight Rebuild Module 23 Test Plan

Date: 2026-06-25

## Module

Tenant Guardrail Middleware Activation

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API and rebuild tests remain compatible.
2. Existing Module 7 through Module 22 tests remain compatible.
3. Tenant guardrails are disabled by default.
4. Disabled tenant guardrails preserve existing commercial headers.
5. Enabled observe mode adds tenant headers without blocking.
6. Enabled blocking mode blocks missing tenant entitlement.
7. Enabled blocking mode allows configured local entitlement.
8. Health details reports tenant guardrail settings.
9. Local entitlement builder uses configured plan.
10. Activation summary reports default behavior change.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 23 status as `passed`.
- Evidence includes implementation files, tests, product guide, test plan, execution report, latest test result, and bootstrap log.
- Exactly one official Module 23 bootstrap entrypoint exists.
- Module 23 bootstrap uses `app.evidence_harness` to write evidence.

## Expected Unit Test Count

The current full repository unittest discovery suite should run 130 tests after Module 23.

- Module 23 tenant middleware tests added in this module: 8
- Expected full-suite total: 130
