# Insight Rebuild Module 32: Local Manifest Checksum

Date: 2026-06-26

## Status

accepted

## Acceptance Evidence

- Evidence commit: `87664a2`
- Product base: `80ee7ab700e3ab124b29472c6523d6e5622a1172`
- Bootstrap: `2026-06-26-insight-rebuild-module-32-official`
- Test command: `python3 -m unittest discover -s tests -p test_*.py -q`
- Result: passed
- Expected test count: 187

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

## Verified Evidence

- `reports/testing/latest_test_result.json`
- `reports/testing/insight_rebuild_module_32_test_result.json`
- `reports/execution/insight_rebuild_module_32_execution_report.md`
