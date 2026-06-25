# ORIS Page Loop Engineering Guide

Date: 2026-06-25

## Purpose

This guide applies bounded Loop Engineering to ORIS product pages and insight workflows. A loop is treated as a repeatable agent workflow that can plan, execute, review, and improve artifacts without requiring a new human prompt for every step.

## Default ORIS Page Loop

1. Read current page or product artifact.
2. Evaluate reusable GitHub/OpenClaw skills and harness components first.
3. Produce a bounded improvement plan.
4. Apply only low-risk local edits.
5. Run tests or document checks.
6. Write machine-readable evidence.
7. Stop and require human acceptance before marking the module accepted.

## Required Gates

- Budget gate: each loop must define maximum iterations and token budget.
- Evidence gate: each loop must produce test or report evidence.
- Safety gate: no live provider, remote runtime, managed database, or payment behavior is enabled by default.
- Reuse gate: reusable skills, harnesses, and AGENTS.md/agent.md templates are evaluated before custom code.
- Acceptance gate: user-controlled bootstrap evidence is required before accepted status.

## Recommended Loop Roles

- Builder: proposes and applies bounded changes.
- Reviewer: checks correctness, safety, and evidence.
- Harness: runs deterministic tests and writes evidence.
- Operator: confirms acceptance using pushed evidence.

## Non-Goals

- Infinite autonomous loops.
- Hidden live network actions.
- Secret access without explicit boundary.
- Direct production deployment.
- Replacing evidence with self-reported success.
