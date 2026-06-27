# Engineering Guardrails

Last updated: 2026-06-27.

This document defines mandatory engineering rules for the commercial ORIS insight employee project.

## 1. Mainline Policy

Production execution must have one mainline logic path.

Do not introduce:

- Duplicate function definitions.
- Duplicate variable definitions with overlapping meaning.
- Hidden compatibility branches.
- Old production code paths left active after replacement.
- Parallel implementations of the same feature.
- Runtime fallback logic that masks architectural drift.

Legacy logic can be backed up in GitHub documentation or archival files, but the production runtime must remain clean and single-path.

## 2. Layering and Separation

Use layered, decoupled design:

- Domain layer: business rules and core concepts.
- Application layer: orchestration and workflows.
- Infrastructure layer: database, model, queue, file, third-party service adapters.
- Interface layer: API, UI, CLI, and external entry points.
- Configuration layer: deployment-specific values outside business logic.

No layer should casually import across boundaries. Cross-layer dependency direction should be explicit and stable.

## 3. Configuration and Secrets

- Deployment-specific configuration must not be hardcoded in production logic.
- Secrets must not be committed.
- Configuration that varies by deployment should be externalized.
- Internal wiring that does not vary by deployment can stay in code.
- Environment and runtime configuration should be documented and auditable.

This follows Twelve-Factor principles for separating config from code and separating build, release, and run stages.

## 4. Testing and Evidence

Every OTA or release step must leave evidence.

Required evidence:

- Machine-readable test result.
- Human-readable execution report.
- Commit SHA for the product base.
- Explicit flags for external calls, release publication, and default behavior changes.

A module is not accepted unless evidence files agree.

## 5. Commercial Readiness

Future product work must consider:

- Tenant isolation.
- Authorization and audit trail.
- Data lifecycle and backup/restore.
- Observability and operational readiness.
- Cost visibility.
- Security-by-design.
- Replaceable infrastructure adapters.
- Clear product module ownership.

Avoid patchwork changes that solve one symptom while creating duplicate paths or hidden state.

## 6. Security Requirements

Use secure-by-default implementation:

- Validate and normalize inputs at boundaries.
- Centralize authentication and authorization decisions.
- Avoid leaking sensitive data in logs.
- Handle errors explicitly without exposing internals.
- Pin and review dependencies.
- Treat external services as replaceable adapters.
- Maintain auditability for data access and operational actions.

OWASP secure coding practices should be used as a baseline for implementation review.

## 7. Cloud and Operations Requirements

Architecture decisions should be reviewed against recognized operational frameworks:

- Operational excellence.
- Security and privacy.
- Reliability and recovery.
- Performance and scalability.
- Cost optimization.
- Sustainability where relevant.

AWS Well-Architected and Google Cloud Architecture Framework are suitable reference anchors even if the deployment is not on AWS or Google Cloud.

## 8. ChatGPT Operating Rules for This Repo

When assisting this project:

- Prefer direct GitHub edits over chat-only plans.
- Keep chat replies short.
- Store long context and design notes in GitHub docs.
- Do not print long generated code unless the user explicitly asks.
- If human server execution is required, provide only the minimal command block.
- Use GitHub evidence files and commits to report status.
- If write operations are blocked, report honestly and provide the smallest manual fallback.

## 9. Review Checklist Before Adding Code

Before modifying production code, check:

- Is there an existing function or module with the same responsibility?
- Will this create a second active path?
- Can old code be removed instead of tolerated?
- Is configuration separated from code?
- Are tests and evidence updated?
- Are security and observability considered?
- Does the change support the commercial product direction?
