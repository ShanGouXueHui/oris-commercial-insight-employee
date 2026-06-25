# Insight Rebuild Module 27: Tenant Usage Admin API

Date: 2026-06-25

## Status

accepted

## Acceptance Evidence

- User-controlled bootstrap final pushed commit: `2b9a7ac57627f3dfd517a3da905ec48d06f6d9c2`
- Evidence commit recorded in report: `03f2b6a2acc162e5882afcda14bba39b9092dbc9`
- Product base commit tested by bootstrap: `12318c835d0a594509b8a2314b859397170c8d27`
- Bootstrap version: `2026-06-25-insight-rebuild-module-27-official`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `160`

## Purpose

Module 27 adds a bounded read-only tenant usage/admin visibility API behind explicit configuration. It preserves default request behavior and does not consume tenant usage.

## Implemented Scope

1. Tenant usage admin API configuration settings.
2. Admin gate protection with masked settings output.
3. Read-only tenant usage endpoint.
4. In-memory tenant usage reads.
5. Explicit SQLite tenant usage reads.
6. Admin endpoint exemption from tenant usage consumption in self-observability scenarios.
7. Health details visibility for the admin API boundary.
8. Unit tests for disabled defaults, gate configuration, invalid access, sensitive-value masking, in-memory reads, SQLite reads, no-consumption read behavior, health details, and access evaluator behavior.
9. Product guide and test plan.
10. Official Module 27 bootstrap script using `app.evidence_harness`.

## Safety Properties

- Tenant usage admin API is disabled by default.
- Admin usage reads require explicit API enablement and a configured admin gate.
- Admin gate values are masked in settings and API payloads.
- Endpoint is read-only and does not call usage consumption.
- No external storage service, billing provider, payment processor, provider call, remote runtime dispatch, or live external database connection is enabled.
- Existing default request behavior remains unchanged.

## Verified Evidence Files

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_27_test_result.json`
- `reports/execution/insight_rebuild_module_27_execution_report.md`
- `reports/execution/insight_rebuild_module_27_bootstrap_latest.log`

## Next Recommended Module After Acceptance

Module 28 should move to a bounded tenant operational audit event trail or admin usage export boundary behind explicit configuration, while preserving default behavior.
