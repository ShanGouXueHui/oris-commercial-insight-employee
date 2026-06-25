# Insight Rebuild Module 25: Tenant Middleware Usage Ledger Bridge

Date: 2026-06-25

## Status

accepted

## Acceptance Evidence

- User-controlled bootstrap final pushed commit: `4adc3defb6c3344c2cdcfd47281864e70a60eb1e`
- Evidence commit recorded in report: `5d3d34e44a088ccbbb8a8b6b6eee73eeeb72a775`
- Product base commit tested by bootstrap: `8ae2f3e0ff95fdf2768eb1b59ef04955352f36e0`
- Bootstrap version: `2026-06-25-insight-rebuild-module-25-official`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `144`

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

## Verified Evidence Files

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_25_test_result.json`
- `reports/execution/insight_rebuild_module_25_execution_report.md`
- `reports/execution/insight_rebuild_module_25_bootstrap_latest.log`

## Next Recommended Module After Acceptance

Module 26 should move to the next controlled commercial operation boundary. Recommended direction: durable tenant usage storage or a bounded tenant usage/admin read API behind explicit configuration, while preserving deterministic local defaults.
