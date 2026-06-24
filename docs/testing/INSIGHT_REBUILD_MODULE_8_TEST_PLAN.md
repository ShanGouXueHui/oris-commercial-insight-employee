# Insight Rebuild Module 8 Test Plan

Date: 2026-06-24

## Module

Durable Evidence Persistence and Database Schema

## Test Command

`python3 -m unittest discover -s tests -p test_*.py -q`

## Required Coverage

1. Existing API surface remains compatible.
2. Existing Module 7 orchestration tests remain compatible.
3. SQLite schema initializes all required evidence persistence tables.
4. SQLite store persists runtime run metadata.
5. SQLite store persists evidence sources.
6. SQLite store persists evidence items.
7. Config-driven `storage_mode=sqlite` selects `SQLiteEvidenceStore`.
8. Runtime v2 adapter can persist an accepted run through SQLite.

## Acceptance Criteria

- Test exit code is `0`.
- `reports/testing/latest_test_result.json` records Module 8 status as `passed`.
- Evidence includes implementation files, tests, test plan, execution report, and latest test result.
- Exactly one official Module 8 bootstrap entrypoint exists.
- No `_v2`, `_v3`, `compat`, or `legacy` main entrypoint is introduced.

## Expected Test Count

- Module 6 API surface tests: 4
- Module 7 orchestration tests: 4
- Module 8 durable persistence tests: 4
- Expected total: 12
