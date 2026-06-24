# Insight Rebuild Module 10: Commercial Guardrails

Date: 2026-06-24

## Status

prepared_pending_local_unit_validation

## Purpose

Module 10 adds commercial API guardrail boundaries before enabling live providers, web/search connectors, or production traffic. The module focuses on auth, quota, rate limit, and structured error policy. It intentionally keeps default behavior non-blocking so existing offline, smoke, and deterministic tests remain compatible.

## Implemented Scope

1. Commercial guardrail settings in `app/config.py`.
2. Commercial guardrail policy engine in `app/commercial_guardrails.py`.
3. FastAPI middleware enforcement boundary in `app/main.py`.
4. Guardrail readiness exposure through runtime observability in `app/observability.py`.
5. Rebuild acceptance payload exposure in `app/rebuild_api.py`.
6. Module 10 unit tests.
7. Official Module 10 bootstrap script.

## Guardrail Settings

`CommercialGuardrailsSettings` includes:

- `enforcement_mode`
- `require_api_key`
- `accepted_api_keys`
- `rate_limit_per_minute`
- `quota_per_day`
- `default_client_id`
- `error_policy`
- `exempt_paths`

Environment variables:

```bash
ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT=observe
ORIS_INSIGHT_REQUIRE_API_KEY=false
ORIS_INSIGHT_API_KEYS=comma,separated,keys
ORIS_INSIGHT_RATE_LIMIT_PER_MINUTE=60
ORIS_INSIGHT_QUOTA_PER_DAY=1000
ORIS_INSIGHT_DEFAULT_CLIENT_ID=anonymous
ORIS_INSIGHT_ERROR_POLICY=structured_json
ORIS_INSIGHT_EXEMPT_PATHS=/healthz,/healthz/details,/healthz/observability
```

## Default Mode

Default mode is `observe`.

In `observe` mode:

- commercial endpoints are not blocked;
- guardrail headers are still added;
- policy status is visible through observability;
- existing deterministic tests and smoke tests remain compatible.

## Blocking Mode

Blocking mode is enabled by:

```bash
ORIS_INSIGHT_GUARDRAILS_ENFORCEMENT=blocking
```

When blocking mode is active:

1. If `ORIS_INSIGHT_REQUIRE_API_KEY=true`, commercial endpoints require `x-api-key`.
2. API keys must match `ORIS_INSIGHT_API_KEYS`.
3. Per-minute request limits are enforced.
4. Daily quota is enforced.
5. Structured JSON error payloads are returned for denied requests.
6. Health endpoints remain exempt by default.

## Error Policy

Blocked responses use structured JSON:

```json
{
  "error": {
    "error_code": "api_key_missing",
    "message": "Missing required x-api-key header.",
    "status_code": 401,
    "policy_version": "2026-06-24-module-10"
  },
  "guardrail": {
    "allowed": false,
    "status_code": 401,
    "reason": "api_key_missing"
  }
}
```

## Response Headers

The middleware attaches guardrail headers:

- `X-ORIS-Guardrail-Policy`
- `X-ORIS-Guardrail-Mode`
- `X-ORIS-Guardrail-Reason`
- `X-ORIS-RateLimit-Remaining-Minute`
- `X-ORIS-Quota-Remaining-Day`
- `Retry-After` when blocked by limit/quota

## API Exposure

`GET /healthz/details` includes:

- `module_10_commercial_guardrails=true`
- guardrail policy through observability

`GET /healthz/observability` includes:

- `module_10_commercial_guardrails_ready=true`
- guardrail policy summary

`GET /insights/rebuild/acceptance` includes:

- `module_10_commercial_guardrails=true`
- `commercial_guardrails_boundary=true`
- `commercial_guardrails` settings summary
- `guardrail_policy`

## Explicit Non-Scope

Module 10 does not add:

- real identity provider integration;
- OAuth/OIDC;
- persistent quota ledger;
- distributed rate limiting;
- billing integration;
- tenant database schema;
- live provider/source connector;
- production deployment.

## Acceptance Rule

Module 10 is accepted only after the official bootstrap script runs in the user-controlled local/server environment and pushes unit-test evidence to GitHub.

## Next Recommended Module After Acceptance

Module 11 should focus on one of:

1. authenticated source/model provider adapter behind the guardrail boundary;
2. persistent commercial quota ledger;
3. managed database transition plan;
4. remote ORIS Runtime v2 worker queue integration.
