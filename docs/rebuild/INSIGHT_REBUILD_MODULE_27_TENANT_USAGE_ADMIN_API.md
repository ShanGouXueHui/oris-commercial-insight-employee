# Insight Rebuild Module 27: Tenant Usage Admin API

Date: 2026-06-25

## Status

implemented_pending_user_controlled_evidence

## Purpose

Module 27 adds a bounded read-only tenant usage/admin visibility API behind explicit configuration. It preserves default request behavior and does not consume tenant usage.

## Implemented Scope

1. Tenant usage admin API configuration settings.
2. Admin key protection with masked settings output.
3. Read-only tenant usage endpoint.
4. In-memory tenant usage reads.
5. Explicit SQLite tenant usage reads.
6. Admin endpoint exemption from tenant usage consumption in self-observability scenarios.
7. Health details visibility for the admin API boundary.
8. Unit tests for disabled defaults, key configuration, invalid access, secret masking, in-memory reads, SQLite reads, no-consumption read behavior, health details, and access evaluator behavior.
9. Product guide and test plan.
10. Official Module 27 bootstrap script using `app.evidence_harness`.

## Safety Properties

- Tenant usage admin API is disabled by default.
- Admin usage reads require explicit API enablement and a configured admin key.
- Admin keys are masked in settings and API payloads.
- Endpoint is read-only and does not call usage consumption.
- No external storage service, billing provider, payment processor, provider call, remote runtime dispatch, or live external database connection is enabled.
- Existing default request behavior remains unchanged.

## Acceptance Boundary

This module is not accepted yet. Acceptance requires user-controlled bootstrap execution, pushed GitHub evidence, and verification of:

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_27_test_result.json`
- `reports/execution/insight_rebuild_module_27_execution_report.md`
- `reports/execution/insight_rebuild_module_27_bootstrap_latest.log`

## Expected Test Count

The expected full-suite unittest count after Module 27 is 160.

## Next Recommended Module After Acceptance

Module 28 should move to a bounded tenant operational audit event trail or admin usage export boundary behind explicit configuration, while preserving default behavior.
