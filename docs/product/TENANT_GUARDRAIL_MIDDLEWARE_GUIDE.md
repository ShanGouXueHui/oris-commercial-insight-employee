# Tenant Guardrail Middleware Guide

Date: 2026-06-25

## Purpose

Module 23 activates the tenant entitlement bridge in API middleware behind an explicit configuration flag.

## Default Behavior

Tenant guardrail middleware is disabled by default:

```bash
ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED=false
```

When disabled, requests continue to use the existing commercial guardrail middleware behavior.

## Activation

A local deterministic activation can be configured with:

```bash
ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED=true
ORIS_INSIGHT_TENANT_GUARDRAILS_ENFORCEMENT=blocking
ORIS_INSIGHT_REQUIRE_TENANT_ENTITLEMENT=true
ORIS_INSIGHT_LOCAL_TENANT_ENTITLEMENTS_ENABLED=true
ORIS_INSIGHT_LOCAL_TENANT_ID=tenant-a
ORIS_INSIGHT_LOCAL_TENANT_PLAN=free
```

## Middleware Headers

When tenant guardrails are enabled, responses include:

- `X-ORIS-Tenant-Guardrail-Version`
- `X-ORIS-Tenant-Guardrail-Reason`
- `X-ORIS-Tenant-ID`

Existing commercial guardrail headers are preserved.

## Safety Rules

- Activation requires an explicit environment flag.
- Local deterministic entitlements are the only Module 23 entitlement source.
- No live external action is performed.
- Existing `evaluate_guardrails` remains compatible.
- Health details report tenant guardrail settings for operator visibility.
