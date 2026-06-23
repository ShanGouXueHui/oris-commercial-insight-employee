# Insight Rebuild Module 7: Runtime v2 Orchestration and Real Evidence Source Integration

Date: 2026-06-23

## Status

accepted

## Purpose

Module 7 moves the commercial insight employee from a pure deterministic sample-evidence API into a Runtime v2 aligned product boundary. It does not connect live web/search/model providers yet. Instead, it establishes the product-side contracts that make those integrations safe to add later.

## Implemented Scope

1. Product-side Runtime v2 orchestration adapter contract.
2. Source connector abstraction.
3. Configuration-separated source, model, runtime, API, and evidence persistence settings.
4. Deterministic local source connector for tests and offline acceptance.
5. Future real web/search/model provider boundary with external providers disabled by default.
6. Evidence persistence boundary with in-memory default and filesystem development option.
7. API/runtime integration through `POST /insights/rebuild/brief`.
8. Module 7 unit tests and GitHub evidence reports.

## Architecture Delta

### Configuration Layer

`app/config.py` defines separated settings:

- `ApiSettings`
- `RuntimeSettings`
- `SourceSettings`
- `ModelProviderSettings`
- `EvidencePersistenceSettings`
- `ProductSettings`

External source/model access remains disabled by default:

- `allow_network_sources=false`
- `allow_external_provider=false`
- `provider_mode=deterministic_template`
- `connector_mode=deterministic_local`

### Source Connector Layer

`app/source_connectors.py` introduces:

- `SourceQuery`
- `SourceConnectorMetadata`
- `SourceConnectorResult`
- `EvidenceSourceConnector` protocol
- `DeterministicLocalSourceConnector`
- `FutureExternalSourceConnectorBoundary`

The deterministic local connector produces complete lens coverage across all required analytical lenses and records that no network or external provider was used.

### Runtime Orchestration Layer

`app/runtime_orchestration.py` introduces:

- `RuntimeV2RunRequest`
- `RuntimeV2RunResult`
- `RuntimeV2OrchestrationAdapter` protocol
- `LocalRuntimeV2OrchestrationAdapter`

The adapter executes this deterministic product run path:

1. Build domain contract.
2. Build source query.
3. Fetch normalized raw evidence through the source connector.
4. Ingest evidence.
5. Generate evidence-linked executive brief.
6. Run quality gates.
7. Persist or index evidence through the evidence persistence boundary.
8. Return a Runtime v2 aligned run payload.

### Evidence Persistence Boundary

`app/evidence_persistence.py` introduces:

- `EvidencePersistenceRecord`
- `EvidenceStore` protocol
- `InMemoryEvidenceStore`
- `FileSystemEvidenceStore`

Module 7 keeps `in_memory` as the default so API tests remain deterministic. A filesystem option exists for development smoke runs, while production database/cache selection is intentionally deferred.

## API Integration

Existing endpoint retained:

- `POST /insights/rebuild/brief`

The endpoint still returns the Module 6 compatible top-level fields:

- `company_name`
- `runtime_v2_backed`
- `accepted`
- `recommended_action`
- `confidence_score`
- `brief`
- `quality`

Module 7 adds Runtime v2 integration fields:

- `runtime_run_id`
- `runtime_adapter`
- `source_connector`
- `evidence_persistence`
- `runtime`

Readiness endpoint enhanced:

- `GET /insights/rebuild/acceptance`

It now reports Module 7 orchestration, source connector, config separation, evidence persistence, and external provider boundary status.

## Explicit Non-Scope

The following are not enabled in Module 7:

- live web search;
- external model/provider execution;
- production database persistence;
- cache integration;
- deployment smoke test;
- tenant/auth/quota/rate-limit guardrails.

## Next Recommended Module

Module 8 should choose one of the following commercial hardening directions:

1. durable evidence persistence and database schema; or
2. deployment smoke test and runtime observability; or
3. authenticated source/model provider adapter with strict config and approval gates.
