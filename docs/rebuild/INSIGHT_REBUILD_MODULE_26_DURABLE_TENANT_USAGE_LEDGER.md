# Insight Rebuild Module 26: Durable Tenant Usage Ledger

Date: 2026-06-25

## Status

implemented_pending_user_controlled_evidence

## Purpose

Module 26 adds optional durable local tenant usage storage behind explicit configuration. It preserves the existing in-memory tenant usage ledger as the deterministic default.

## Implemented Scope

1. Tenant usage ledger storage configuration settings.
2. SQLite-backed tenant usage ledger.
3. SQLite schema initialization and metadata records.
4. Durable usage consumption and retrieval by tenant and monthly period.
5. Tenant usage ledger builder that keeps in-memory default behavior.
6. Middleware bridge using the configured tenant usage ledger when tenant usage is explicitly enabled.
7. Health details visibility for durable tenant usage storage.
8. Unit tests for defaults, persistence, metadata, builder behavior, summary flags, middleware persistence, and health details.
9. Product guide and test plan.
10. Official Module 26 bootstrap script using `app.evidence_harness`.

## Safety Properties

- In-memory tenant usage ledger remains the default.
- SQLite storage is only enabled through explicit configuration.
- SQLite is local durable storage, not a live managed database service.
- No external billing provider, payment processor, provider call, remote runtime dispatch, or live external database connection is enabled.
- Tenant guardrail and tenant usage middleware behavior still require explicit flags.

## Acceptance Boundary

This module is not accepted yet. Acceptance requires user-controlled bootstrap execution, pushed GitHub evidence, and verification of:

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_26_test_result.json`
- `reports/execution/insight_rebuild_module_26_execution_report.md`
- `reports/execution/insight_rebuild_module_26_bootstrap_latest.log`

## Expected Test Count

The expected full-suite unittest count after Module 26 is 151.

## Next Recommended Module After Acceptance

Module 27 should move to a bounded tenant usage/admin read API or operational visibility surface behind explicit configuration, without changing default request behavior.
