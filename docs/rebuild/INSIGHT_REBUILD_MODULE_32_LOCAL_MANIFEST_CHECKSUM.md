# Insight Rebuild Module 32: Local Manifest Checksum

Date: 2026-06-26

## Status

implemented_pending_execution_evidence

## Purpose

Module 32 adds local checksum visibility for local manifests.

## Scope

- Checksum helper added to `app/tenant_operational_audit_retention.py`.
- Tests added in `tests/test_module_32_local_manifest_checksum.py`.
- Runner added at `scripts/m32.sh`.
- Writer added at `scripts/w32.py`.

## Safety

- Disabled by default.
- Local checksum visibility only.
- No file export is written.
- Existing request behavior remains unchanged.

## Expected Test Count

187
