# Insight Rebuild Module 17: Reusable Skills and Harness Adoption Boundary

Date: 2026-06-25

## Status

accepted

## Acceptance Evidence

- Local validation evidence commit: `57acd03e0c33af6c337bd7003d924478a14175fa`
- Evidence commit recorded in report: `bd2167ef84c05a6c5c3e80ffab2563dbdd4e1d6a`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Test exit code: `0`
- Expected unit test count: `63`

## Purpose

Module 17 changes the engineering default from custom-first to reuse-first. It introduces a repeatable adoption boundary for GitHub skills, OpenClaw skills, harness upgrades, and AGENTS.md or agent.md templates before further product scaffolding is built.

## Implemented Scope

1. Reuse candidate contract.
2. Candidate categories for GitHub skill, OpenClaw skill, harness, and AGENTS.md template.
3. Reuse score calculation.
4. Adopt, fork-and-adapt, defer, and reject decisions.
5. License, maintenance, security, product-boundary, network, and secret checks.
6. Default candidate set for skills, harness, AGENTS.md, and live-provider skill boundary.
7. Reuse adoption plan summary.
8. Project `AGENTS.md` with repo operating rules.
9. Unit tests for high-quality adoption, license rejection, network/secret penalty, harness and AGENTS.md presence, reuse-first defaults, summary counts, and scoring penalty.
10. Official Module 17 bootstrap script.

## Adoption Rule

Reusable components should be considered before new custom code. Direct adoption is allowed only if the component passes license, maintenance, security, product-boundary, and secret-handling checks.

## Harness Rule

OpenClaw and related harness components should be upgraded or reused when they improve reliability, evidence quality, execution control, or safety boundaries.

## AGENTS.md Rule

AGENTS.md or agent.md templates may be reused or adapted when they improve repeatability and do not conflict with project-specific acceptance and safety rules.

## Safety Properties

- Custom code is no longer the default.
- Components requiring network or secrets are penalized unless wrapped by explicit boundaries.
- Credentials must not be logged, reported, or summarized.
- A candidate with unacceptable license or weak security signal is rejected.
- Live behavior remains disabled unless a later module explicitly enables and validates it.

## Explicit Non-Scope

Module 17 does not add:

- automatic third-party code import;
- package installation;
- live skill registry sync;
- live OpenClaw upgrade execution;
- live provider calls;
- live remote queue dispatch.

## Next Recommended Module After Acceptance

Module 18 should focus on Loop Engineering adoption for ORIS pages and harness orchestration, using reusable skills/OpenClaw components first and keeping all loops bounded by evidence, budget, and safety gates.
