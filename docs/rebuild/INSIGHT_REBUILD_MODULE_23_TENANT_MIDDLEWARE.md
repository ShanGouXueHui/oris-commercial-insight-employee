# Insight Rebuild Module 23: Tenant Guardrail Middleware Activation

Date: 2026-06-25

## Status

accepted

## Acceptance Evidence

- Local validation evidence commit: `a44da751b6cdbf0fe4b56ba9f3d4020e59c60ff5`
- Evidence commit recorded in report: `8ae78b3aa4de9ab458e90f7c1b20b5062e0ec9b5`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `130`

## Purpose

Module 23 activates the Module 22 tenant entitlement bridge in API middleware behind an explicit configuration flag. Default production behavior remains unchanged when the flag is disabled.

## Implemented Scope

1. Tenant guardrail settings in product configuration.
2. Explicit `ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED` activation flag.
3. Local deterministic tenant entitlement settings.
4. Tenant guardrail policy adapter from settings.
5. Local entitlement builder from settings.
6. Middleware branch for tenant guardrail evaluation.
7. Tenant guardrail response headers.
8. Health details tenant settings visibility.
9. Tenant Guardrail Middleware Guide.
10. Unit tests for default disabled behavior, existing header compatibility, observe activation, blocking missing entitlement, blocking valid entitlement, health details, local entitlement builder, and activation summary.
11. Official Module 23 bootstrap script using the evidence harness helper.

## Default Behavior

Tenant middleware activation is disabled by default. Existing commercial guardrail behavior remains active and compatible.

## Activation Flags

- `ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED`
- `ORIS_INSIGHT_TENANT_GUARDRAILS_ENFORCEMENT`
- `ORIS_INSIGHT_REQUIRE_TENANT_ENTITLEMENT`
- `ORIS_INSIGHT_LOCAL_TENANT_ENTITLEMENTS_ENABLED`
- `ORIS_INSIGHT_LOCAL_TENANT_ID`
- `ORIS_INSIGHT_LOCAL_TENANT_PLAN`

## Safety Properties

- Existing commercial guardrail behavior remains default.
- Existing `evaluate_guardrails` signature remains unchanged.
- Local deterministic entitlements are the only Module 23 entitlement source.
- No live external action is performed.
- Tenant guardrail headers are emitted only when tenant guardrails are enabled.

## Explicit Non-Scope

Module 23 does not add:

- external entitlement source;
- production tenant database lookup;
- invoice generation;
- tax calculation;
- live provider calls;
- live remote runtime dispatch.

## Next Recommended Module After Acceptance

Module 24 should focus on a local tenant entitlement usage ledger so enabled tenant middleware can consume deterministic monthly usage without external storage.
