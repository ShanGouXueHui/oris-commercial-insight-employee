# Bootstrap Migration Guide

Date: 2026-06-25

## Purpose

This guide defines how older official bootstrap scripts should be migrated to the reusable evidence harness helper introduced in Module 20.

## Migration Principle

Migrate one low-risk bootstrap at a time. Do not rewrite all historical scripts in one step. Every migration must be covered by tests and verified through user-controlled bootstrap evidence.

## Required Pattern

A migrated bootstrap should:

1. keep the existing command-line entrypoint name;
2. keep short terminal output;
3. keep the same test command style;
4. use `app.evidence_harness` to write JSON evidence and execution report;
5. use `record_evidence_commit_sha` for the second evidence commit;
6. avoid package installation, remote code fetch, and production harness changes.

## Module 21 Selected Migration

Module 21 migrates:

- `scripts/bootstrap_insight_rebuild_module_19.sh`

Reason: Module 19 is recent, boundary-only, and its evidence structure maps directly to the Module 20 helper.

## Safety Rules

- Preserve accepted module documentation.
- Do not change product runtime behavior.
- Do not run live external actions.
- Do not expose secrets in evidence.
- Do not mark migrated scripts accepted without fresh evidence.
