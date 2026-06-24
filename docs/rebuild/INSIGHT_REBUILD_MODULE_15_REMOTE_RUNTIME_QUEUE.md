# Insight Rebuild Module 15: Remote Runtime v2 Worker Queue Boundary

Date: 2026-06-24

## Status

prepared_pending_local_unit_validation

## Purpose

Module 15 adds a product-side remote Runtime v2 worker queue boundary. It prepares the job contract and adapter seam for a future remote ORIS Runtime v2 worker, while keeping local Runtime v2 execution active by default.

## Implemented Scope

1. Remote runtime queue settings.
2. Remote runtime job contract.
3. Remote queue readiness contract.
4. Disabled/default queue adapter for local runtime safety.
5. Remote boundary queue adapter.
6. Deterministic job ID generation.
7. Local enqueue/status behavior without remote dispatch.
8. Credential and endpoint presence detection without exposing credentials.
9. Unit tests for default safety, enqueue/status, missing endpoint, missing credential, configured boundary, blocked dispatch flag, credential redaction, and deterministic job ID.
10. Official Module 15 bootstrap script.

## Queue Modes

### `disabled`

Default mode. Local Runtime v2 remains active. No remote dispatch is attempted.

### `remote_boundary`

Boundary mode for future remote Runtime v2 worker integration. It can detect endpoint and credential configuration, but it intentionally does not dispatch remotely in Module 15.

## Environment Variables

```bash
ORIS_REMOTE_RUNTIME_QUEUE_MODE=disabled
ORIS_REMOTE_RUNTIME_QUEUE_NAME=insight-runtime-v2
ORIS_RUNTIME_QUEUE_ENDPOINT=<configured only in private runtime>
ORIS_RUNTIME_QUEUE_TOKEN=<configured only in private runtime>
ORIS_REMOTE_RUNTIME_DISPATCH_ENABLED=false
```

## Safety Properties

- Default behavior remains local Runtime v2 execution.
- Remote dispatch is not implemented in Module 15.
- Credentials are detected only as configured/not configured.
- Credentials are never returned in summaries.
- Enqueue/status calls remain local boundary behavior.
- If dispatch is explicitly enabled, Module 15 blocks readiness because live dispatch is not implemented.

## Explicit Non-Scope

Module 15 does not add:

- live remote queue dispatch;
- remote worker execution;
- queue transport SDK;
- retry/backoff engine;
- distributed tracing;
- production secret manager integration;
- tenant billing schema.

## Acceptance Rule

Module 15 is accepted only after the official bootstrap script runs in the user-controlled local/server environment and pushes unit-test evidence to GitHub.

## Next Recommended Module After Acceptance

Module 16 should focus on one of:

1. tenant and billing schema;
2. remote runtime queue live smoke in a controlled non-production environment;
3. provider-backed generation smoke with explicitly configured safe credentials;
4. production deployment packaging.
