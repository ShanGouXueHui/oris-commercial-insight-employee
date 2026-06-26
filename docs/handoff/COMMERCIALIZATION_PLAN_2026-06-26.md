# Commercialization Plan

Date: 2026-06-26

## Current state

The rebuild has 61 accepted modules and 303 expected tests. The latest accepted module is Module 61: local capsule summary visibility.

The project is ready to pivot from incremental local visibility modules to commercial product hardening.

## Recommended next workstreams

1. Product flow: define the commercial user journey, tenant onboarding, insight generation, review, export, and audit flows.
2. Data model: harden tenant, workspace, project, insight, evidence, execution, audit, and billing-related entities.
3. API surface: define versioned internal APIs and public commercial APIs, with stable schemas.
4. Storage: identify current local-only paths and plan database-backed persistence where needed.
5. Security: RBAC, tenant isolation, secrets, safe logging, audit trail, and data retention.
6. Observability: health checks, metrics, run IDs, traceable execution reports, and failure diagnostics.
7. Deployment: production configuration, one active main branch, backup only when needed, rollback plan.
8. Packaging: commercial edition boundaries, license gates if needed, documentation, and operator runbook.

## Suggested immediate next module

Module 62 should not continue the cosmetic naming chain unless explicitly required. Recommended Module 62: commercial readiness baseline.

Proposed Module 62 scope:

- Add a local-only `app/commercial_readiness.py` helper.
- Summarize readiness dimensions: tests, docs, safety, configuration, storage, API, security, observability.
- Default disabled through `ORIS_COMMERCIAL_READINESS_ENABLED`.
- No external calls, no release publish, no file export from the helper.
- Add tests and evidence writer.

## Unfinished items to carry forward

- Decide whether to continue micro-module sequence or pivot to commercial readiness.
- Review and clean stale pending docs only when evidence exists.
- Optionally clean stray Module 9 sqlite runtime evidence if confirmed safe.
- Add architecture docs for commercial tenant/data/API model.
- Add deployment and operations guide.
- Add security baseline and audit policy.
