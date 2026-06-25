# AGENTS.md

## Project

`oris-commercial-insight-employee` is the Insight Product / Commercial Insight Employee product repo.

## Operating Principle

Prefer high-quality reusable skills, harnesses, and project instruction templates before writing custom scaffolding. Custom code is acceptable only when the reusable option fails product boundary, security, license, maintainability, or evidence requirements.

## Required Workflow

1. Read persistent project context before changing architecture.
2. Keep all product changes in this repository.
3. Preserve deterministic local behavior by default.
4. Do not enable live network, provider, database, payment, or remote worker behavior unless a module explicitly enables it and evidence proves it.
5. For every module, provide implementation, tests, docs, and an official bootstrap script.
6. The official bootstrap must write `reports/testing/latest_test_result.json` and an execution report.
7. Do not mark a module accepted until evidence from the user-controlled environment is pushed and verified.

## Reuse Policy

Before building a new local abstraction, evaluate:

- GitHub skills or actions with strong adoption signals;
- OpenClaw skills or harness components;
- existing project harnesses;
- AGENTS.md or agent.md templates from credible engineering projects.

A reusable component can be adopted only when:

- license is acceptable;
- maintenance signal is sufficient;
- security signal is sufficient;
- it fits the product boundary;
- it does not silently enable live external behavior;
- secrets are never exposed in logs, reports, summaries, or responses.

## Safety Defaults

- Local deterministic execution remains the default.
- SQLite/local persistence remains the default until explicitly replaced.
- Live provider calls remain disabled by default.
- Live remote runtime dispatch remains disabled by default.
- Managed database live connections remain disabled by default.
- Tenant entitlement logic is boundary-only until integrated into guardrails.

## Evidence Rules

Evidence must be explicit and machine-readable. The current acceptance signal is `reports/testing/latest_test_result.json` with module name, status, test command, exit code, expected unit test count, and relevant module flags.
