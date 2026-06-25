# Evidence Harness Helper Guide

Date: 2026-06-25

## Purpose

Module 20 introduces a reusable evidence harness helper so future official bootstrap scripts can stop duplicating JSON and report-generation logic.

## Helper Responsibilities

- Build `reports/testing/latest_test_result.json`.
- Build module-specific test result JSON.
- Render execution reports.
- Record evidence commit SHA after the first evidence commit.
- Redact sensitive values from evidence payloads.
- Keep module acceptance fields consistent across modules.

## Required Fields

Every module result should include:

- module name;
- bootstrap version;
- status;
- generated timestamp;
- test command;
- test exit code;
- product base SHA;
- expected unit test count;
- checks;
- log file path.

## Safety Rules

- Do not include raw credentials in JSON evidence.
- Do not include raw tokens in reports.
- Do not use evidence helper output as acceptance unless the user-controlled environment pushed it.
- The helper does not perform external actions.

## Migration Rule

New modules should use `app.evidence_harness` by default. Older module scripts may remain unchanged until a bounded harness cleanup module migrates them.
