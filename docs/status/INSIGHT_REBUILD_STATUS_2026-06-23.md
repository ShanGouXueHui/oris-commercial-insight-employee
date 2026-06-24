# Insight Rebuild Status - 2026-06-24

## Context

The ORIS Autonomous Dev Employee Runtime v2 has completed final acceptance in `ShanGouXueHui/oris`. The product repo `ShanGouXueHui/oris-commercial-insight-employee` has completed the first Runtime v2 backed rebuild stage, Module 7 commercialization boundary work, Module 8 durable evidence persistence, and Module 9 deployment smoke plus runtime observability acceptance. Module 10 commercial guardrail code is prepared and pending local unit validation evidence.

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
   - `reports/testing/latest_test_result.json` showed `status=passed`, `test_exit_code=0`, and `first_stage_rebuild_closed=true`.

7. Module 7: Runtime v2 Orchestration and Real Evidence Source Integration
   - Implementation base commit: `a64b859c90594925d632b3c04a4c2f5fae163f85`
   - Evidence commit: `ddc33b79b6213559a3edbb0cb7ce87a0e02eb4c2`
   - Execution report commit: `7882f6425f374c9ea1a164cc1a52ee61cf47d8ea`
   - `reports/testing/latest_test_result.json` showed `status=passed`, `test_exit_code=0`, and `local_validation_test_count=8`.

8. Module 8: Durable Evidence Persistence and Database Schema
   - Implementation base commit: `6d5674bb0776e3cf78fd53d010930775d2d0d63b`
   - Evidence commit: `974a6f71c4dac5463a3da77c759cd3bdb76c6cf8`
   - Execution report commit: `30647144b5f093618234b73f956c7268b22480c1`
   - `reports/testing/latest_test_result.json` shows `status=passed`, `test_exit_code=0`, and `expected_test_count=12`.

9. Module 9: Deployment Smoke Test and Runtime Observability
   - Preparation base commit: `9181e7a634e8b40357c815b89e899473533de145`
   - Local smoke evidence commit: `80b2b40a04a0711ad76bf1b7f9a2867a8cb21155`
   - Evidence commit recorded in report: `3b34c5ab4d6bf3937c6aef98869c25be6357033e`
   - Official bootstrap script: `scripts/bootstrap_insight_rebuild_module_9.sh`
   - `reports/testing/latest_test_result.json` shows `status=passed`, `unit_test_exit_code=0`, `smoke_test_exit_code=0`, and `expected_unit_test_count=16`.
   - `reports/testing/insight_rebuild_module_9_smoke_result.json` shows health, observability, rebuild acceptance, rebuild brief, and SQLite persistence count checks passed.

## Prepared Pending Module

10. Module 10: Commercial Guardrails
   - Preparation status: `prepared_pending_local_unit_validation`
   - Prepared code/docs/script base commit: `aa8b3711f492fa369195edbd06b01690622938d3`
   - Official bootstrap script: `scripts/bootstrap_insight_rebuild_module_10.sh`
   - Acceptance requires the official bootstrap to run in the user-controlled local/server environment and push GitHub evidence.

## Current Product Capabilities

- FastAPI API version: `0.2.0`.
- Legacy endpoint retained: `POST /insights/executive-brief`.
- Runtime v2 backed readiness endpoint: `GET /insights/rebuild/acceptance`.
- Runtime v2 backed brief endpoint: `POST /insights/rebuild/brief`.
- Domain contracts exist for subject, evidence source, evidence item, brief section, quality gates, and required analytical lenses.
- Deterministic evidence ingestion exists.
- Deterministic brief generation pipeline exists.
- Deterministic quality gates exist.
- Product-side Runtime v2 orchestration adapter exists.
- Source connector abstraction exists.
- Config-separated source/model/runtime/API/evidence settings exist.
- Deterministic local source connector exists for tests and offline acceptance.
- Future external web/search/model provider boundary exists but remains disabled by default.
- Evidence persistence boundary exists with in-memory, filesystem, and SQLite options.
- SQLite durable evidence schema exists with `persistence_metadata`, `runtime_runs`, `evidence_sources`, and `evidence_items` tables.
- Runtime adapter can persist evidence through SQLite when configured.
- Runtime observability snapshot exists.
- `/healthz/observability` exists.
- Local deployment smoke test has passed against uvicorn on `127.0.0.1:8099`.
- SQLite smoke persistence produced one runtime run, three evidence sources, and nine evidence items.
- Commercial guardrail settings exist for API key, quota, rate limit, default client ID, structured error policy, and exempt paths.
- Commercial guardrail middleware exists in default observe mode and optional blocking mode.
- Commercial guardrail readiness is exposed through `/healthz/details`, `/healthz/observability`, and `/insights/rebuild/acceptance`.
- API acceptance, Module 7 orchestration tests, Module 8 durable persistence tests, and Module 9 deployment smoke tests pass.

## Current Limitations

- Module 10 is prepared but not accepted until local unit evidence is pushed.
- Evidence source integration is still deterministic local only.
- No live public web/search connector is enabled.
- SQLite is a durable local/deployment-smoke store, not a managed production database.
- No production cache is configured.
- No external model/provider adapter is enabled.
- Runtime v2 orchestration is product-side/local-contract aligned, not yet executing through a remote ORIS runtime worker queue.
- No production deployment has been completed; Module 9 validated local deployment smoke only.
- Module 10 guardrail ledger is in-memory and not yet persistent or distributed.

## Next Step

Run the official Module 10 bootstrap script in the user-controlled local/server environment. After it pushes evidence, read:

1. `reports/testing/latest_test_result.json`
2. `reports/testing/insight_rebuild_module_10_test_result.json`
3. `reports/execution/insight_rebuild_module_10_execution_report.md`

Then mark Module 10 accepted if `status=passed` and `test_exit_code=0`.
