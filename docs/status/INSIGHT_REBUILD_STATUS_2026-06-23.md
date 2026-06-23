# Insight Rebuild Status - 2026-06-23

## Context

The ORIS Autonomous Dev Employee Runtime v2 has completed final acceptance in `ShanGouXueHui/oris`. The product repo `ShanGouXueHui/oris-commercial-insight-employee` has now completed the first Runtime v2 backed rebuild stage.

## Accepted Product Rebuild Modules

1. Module 1: Architecture Alignment with Runtime v2
   - Final commit: `f31b0f5cfbbe71a9ba13f1ab92a813825641dc0f`
   - Evidence commit: `82f06edfaa4d12f52e97d07189e84d1e6b38948e`

2. Module 2: Domain Contracts
   - Final commit: `21fb37126c5727f9dd0ad3e94b19e004340567cb`
   - Evidence commit: `ffa1e49d9c575994aca038f15ddbd1edd5e18f48`

3. Module 3: Evidence Ingestion
   - Final commit: `589761b65349f5c340457d727c7c314ca0a5f364`
   - Evidence commit: `7e13450574d786a7dd9ecb1cb5c85bfeee96fb62`

4. Module 4: Brief Generation Pipeline
   - Final commit: `dfc9738ac315772c401a5ad9acf0b5400f894201`
   - Evidence commit: `77c20fbcd54993696c873f4a5412a2b4dc3fe6d7`

5. Module 5: Quality Gates and Limitations
   - Final commit: `be403f249730cb4e8743c3e2677030b54dfe8a50`
   - Evidence commit: `e5322e7a0f5e97b05a8d2019ce88f8dc5cd4a1c2`

6. Module 6: API Surface and Acceptance
   - Final commit: `8a66d3858c42721fa44f6bae3c4a66b7140f569b`
   - Evidence commit: `0a7cca536c42470ca2c551dcdede6c4fc8441f26`
   - `reports/testing/latest_test_result.json` shows `status=passed`, `test_exit_code=0`, and `first_stage_rebuild_closed=true`.

## Current Product Capabilities

- FastAPI API version: `0.2.0`.
- Legacy endpoint retained: `POST /insights/executive-brief`.
- Runtime v2 backed readiness endpoint: `GET /insights/rebuild/acceptance`.
- Runtime v2 backed brief endpoint: `POST /insights/rebuild/brief`.
- Domain contracts exist for subject, evidence source, evidence item, brief section, quality gates, and required analytical lenses.
- Deterministic evidence ingestion exists.
- Deterministic brief generation pipeline exists.
- Deterministic quality gates exist.
- API acceptance tests pass.

## Current Limitations

- Evidence source integration is still sample/local deterministic only.
- No production database is configured.
- No cache is configured.
- No external model/provider adapter is integrated in the product repo yet.
- Runtime v2 orchestration is accepted in ORIS, but the product has not yet been wired to an ORIS runtime run/executor path.
- No production deployment smoke test has been completed for the product.

## Next Module

Insight Rebuild Module 7: Runtime v2 Orchestration and Real Evidence Source Integration.

Expected focus:

- product-side orchestration adapter contract;
- source connector configuration contract;
- real evidence source abstraction;
- config separation for API/runtime/model/source settings;
- deterministic local source implementation for tests;
- boundary for future web/search/model providers;
- Runtime v2 run/evidence alignment report;
- tests and GitHub evidence.
