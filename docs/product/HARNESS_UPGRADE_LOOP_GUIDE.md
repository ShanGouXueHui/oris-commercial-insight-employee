# Harness Upgrade Loop Guide

Date: 2026-06-25

## Purpose

This guide defines how ORIS should evaluate OpenClaw, GitHub, and harness upgrade candidates before adding more custom execution scaffolding.

## Loop Steps

1. Discover reusable harness, skill, or instruction-template candidates.
2. Assess license, maintenance, security, product-boundary fit, network requirements, and secret requirements.
3. Plan an isolated worktree or branch for future adoption.
4. Define deterministic tests and evidence requirements.
5. Produce machine-readable evidence.
6. Stop for user-controlled bootstrap validation and acceptance.

## Default Candidates

- OpenClaw execution harness upgrade.
- AGENTS.md or agent.md operating rules upgrade.

## Safety Rules

- No package installation in the planning module.
- No remote code fetch in the planning module.
- No production harness modification in the planning module.
- No hidden network action.
- No secret access.
- User-controlled evidence remains required before accepted status.

## Upgrade Criteria

A harness upgrade may proceed only when it improves at least one of:

- reliability;
- evidence quality;
- execution isolation;
- skill reuse;
- loop orchestration;
- operator acceptance clarity.
