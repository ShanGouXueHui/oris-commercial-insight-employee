# Engineering and Commercialization Rules - 2026-06-23

## Operating Environment

- Product repo: `ShanGouXueHui/oris-commercial-insight-employee`.
- ORIS runtime repo: `ShanGouXueHui/oris`.
- Default local workspace: `/home/admin/projects`.
- Current product local path: `/home/admin/projects/oris-commercial-insight-employee`.
- Current ORIS local path: `/home/admin/projects/oris`.
- Runtime v2 final ORIS reference: `896bdc67942a27cea98b8a4eb8f49d946795a741`.
- Product first-stage rebuild final reference: `8a66d3858c42721fa44f6bae3c4a66b7140f569b`.
- Historical development environment: Singapore server `43.106.55.255`, user `cpsdev`.
- Historical production environment: Hangzhou server `8.136.28.6`, user `deploy`; do not touch unless explicitly authorized.

## Interaction Rules

- Prefer direct GitHub updates for design, docs, scripts, and memory.
- Do not ask the user for confirmation at every module boundary.
- Ask the user to run commands only when the step requires the user's authenticated/local server execution.
- Keep user-facing terminal commands short.
- Do not ask the user to paste long logs.
- Read reports and logs from GitHub evidence after scripts push them.

## Branch and Script Rules

- Keep one mainline branch unless a specific PR workflow is explicitly needed.
- Maintain exactly one official executable entry point per workflow/module.
- Do not create `_v2.sh`, `_v3.sh`, `compat.sh`, `legacy.sh`, or similar duplicated official scripts.
- Git history is the backup mechanism.
- Do not use `set -e` in user-facing shell scripts or copy-paste commands.

## Architecture Rules

- Keep layers decoupled:
  - API layer: FastAPI routers and request/response contracts.
  - Domain layer: product domain contracts and analytical lenses.
  - Ingestion layer: evidence source normalization and validation.
  - Pipeline layer: brief generation.
  - Quality layer: confidence gates, evidence linkage, limitations, action recommendation.
  - Orchestration layer: Runtime v2/run/evidence integration.
- Keep configuration separate from business logic.
- Do not hardcode one company, one customer, or one private source into the generic product path.
- The product should remain a reusable commercial version.
- External model/provider/source integration must be behind adapter/config boundaries.

## Evidence and Acceptance Rules

Every module requires:

- implementation files;
- tests;
- test plan or rebuild doc;
- execution report;
- `reports/testing/latest_test_result.json`;
- pushed GitHub evidence commit.

A module is not accepted from terminal text alone. GitHub evidence is authoritative.

## Commercialization Direction

The product should now move from deterministic local sample evidence toward commercial capability:

1. Runtime v2 orchestration adapter.
2. Real source connector abstraction.
3. Config-separated provider/source settings.
4. Durable evidence store or database design.
5. API readiness and deployment smoke tests.
6. Multi-tenant/commercial guardrails: auth, quota, rate limits, observability, error policy.
