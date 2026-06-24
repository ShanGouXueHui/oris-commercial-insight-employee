# Insight Rebuild Module 12: Provider Adapter Boundary

Date: 2026-06-24

## Status

accepted

## Acceptance Evidence

- Local validation evidence commit: `3aa0a69dfd23c13092f0f1339dfb6957ec2f26e4`
- Evidence commit recorded in report: `d7de7d26a8e231db2438d8f3e0c61b3d41b5d71e`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `30`

## Purpose

Module 12 adds a provider adapter boundary before enabling any live model provider. The goal is to create a safe integration seam that supports deterministic local mode by default, validates external-provider readiness, and avoids leaking credentials.

## Implemented Scope

1. Provider request and response contracts.
2. Deterministic local provider adapter.
3. External provider boundary adapter.
4. Provider adapter builder.
5. Provider readiness summary.
6. Unit tests for deterministic mode, disabled external mode, missing credential handling, and credential redaction.
7. Official Module 12 bootstrap script.

## Provider Modes

### `deterministic_template`

Default local mode. It does not use network access and does not require credentials.

### `external_boundary`

Boundary-only mode. It validates configuration and credentials, but intentionally does not perform live calls.

## Environment Variables

```bash
ORIS_INSIGHT_MODEL_PROVIDER=deterministic_template
ORIS_INSIGHT_ALLOW_EXTERNAL_MODEL_PROVIDER=false
ORIS_INSIGHT_DEFAULT_MODEL=none
ORIS_INSIGHT_PROVIDER_API_KEY=<configured only in private runtime>
```

## Safety Properties

- Default behavior remains deterministic and local.
- External provider calls are not implemented in Module 12.
- Credentials are detected only as configured/not configured.
- Credentials are not returned in summaries.
- External provider usage remains false in boundary-only responses.

## Explicit Non-Scope

Module 12 does not add:

- live model/provider calls;
- live web/search calls;
- provider SDK dependency;
- streaming response support;
- provider cost accounting;
- production secret manager integration;
- tenant billing.

## Next Recommended Module After Acceptance

Module 13 should focus on one of:

1. provider-backed generation smoke with an explicitly configured safe provider;
2. managed production database transition;
3. remote ORIS Runtime v2 worker queue integration;
4. tenant and billing schema.
