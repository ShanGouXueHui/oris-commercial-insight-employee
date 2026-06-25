# Insight Rebuild Module 25: Tenant Middleware Usage Ledger Bridge

Date: 2026-06-25

## Status

implemented_pending_user_controlled_evidence

## Purpose

Module 25 connects the Module 24 tenant usage ledger to the Module 23 tenant middleware behind explicit configuration. Default behavior remains unchanged.

## Implemented Scope

1. Tenant usage ledger middleware configuration flags.
2. Tenant guardrail policy extension for usage ledger read and consume behavior.
3. Tenant middleware entitlement evaluation using ledger usage when explicitly enabled.
4. Allowed-request usage consumption when explicitly enabled.
5. Usage headers for explicit bridge mode.
6. Health details visibility for the Module 25 bridge.
7. Unit tests for defaults, explicit flags, quota blocking, consumption, middleware headers, and exempt-path safety.
8. Product guide and test plan.
9. Official Module 25 bootstrap script using `app.evidence_harness`.

## Safety Properties

- Default tenant usage ledger bridge flags are disabled.
- Tenant guardrails still need explicit activation.
- Exempt paths do not consume tenant usage.
- Blocked tenant requests do not consume tenant usage.
- The ledger remains local and deterministic.
- No external storage, live billing provider, payment processor, provider call, or remote runtime dispatch is enabled.

## Acceptance Boundary

This module is not accepted yet. Acceptance requires user-controlled bootstrap execution, pushed GitHub evidence, and verification of:

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_25_test_result.json`
- `reports/execution/insight_rebuild_module_25_execution_report.md`
- `reports/execution/insight_rebuild_module_25_bootstrap_latest.log`

## Expected Test Count

The expected full-suite unittest count after Module 25 is 144.

## Next Recommended Module After Acceptance

Module 26 should move to the next controlled commercial operation boundary after verifying Module 25 evidence, likely durable tenant usage storage or a bounded tenant admin/read API behind explicit configuration.
