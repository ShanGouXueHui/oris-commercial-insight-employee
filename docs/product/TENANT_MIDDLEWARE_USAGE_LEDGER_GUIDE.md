# Tenant Middleware Usage Ledger Guide

Date: 2026-06-25

## Purpose

Module 25 connects the Module 24 local tenant usage ledger to the Module 23 tenant guardrail middleware behind explicit configuration. Default request-path behavior remains unchanged.

## Configuration

The bridge is disabled by default.

| Setting | Default | Purpose |
| --- | --- | --- |
| `ORIS_INSIGHT_TENANT_USAGE_LEDGER_ENABLED` | `false` | Lets tenant middleware read current monthly tenant usage from the local ledger before entitlement evaluation. |
| `ORIS_INSIGHT_TENANT_USAGE_CONSUME_ON_ALLOWED_REQUEST` | `false` | Lets tenant middleware consume one tenant usage unit only after the tenant guardrail allows the request. |

These flags only matter when `ORIS_INSIGHT_TENANT_GUARDRAILS_ENABLED=true`.

## Runtime Behavior

1. Commercial guardrails still run first.
2. Exempt paths still skip tenant entitlement evaluation and do not consume tenant usage.
3. When the usage ledger flag is enabled, the tenant middleware reads current monthly usage and passes it into entitlement evaluation.
4. When the consume flag is enabled, allowed non-exempt tenant requests increment the local tenant usage ledger.
5. Blocked tenant requests do not consume tenant usage.

## Response Headers

When the tenant usage ledger bridge is explicitly enabled, tenant middleware responses include:

- `X-ORIS-Tenant-Usage-Ledger-Version`
- `X-ORIS-Tenant-Usage-Consumed`
- `X-ORIS-Tenant-Usage-Request-Count` when usage was available

No tenant usage headers are emitted when the bridge is disabled.

## Safety Rules

- No external storage is enabled.
- No live billing provider is integrated.
- No payment processing is enabled.
- Default behavior remains unchanged unless explicit flags are enabled.
