#!/usr/bin/env bash

# Insight Rebuild Module 14 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-24-insight-rebuild-module-14-official"
WORKDIR="${INSIGHT_WORKDIR:-$HOME/projects}"
PRODUCT_DIR="${PRODUCT_DIR:-$WORKDIR/oris-commercial-insight-employee}"
BRANCH="${INSIGHT_BRANCH:-main}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
LOG_FILE=""

summary() { printf '%s\n' "$1"; }

fail_short() {
  summary "FAILED: $1"
  if [ -n "$LOG_FILE" ]; then summary "Log: $LOG_FILE"; fi
  exit 1
}

ensure_git_identity() {
  name="$(git config user.name 2>/dev/null)"
  email="$(git config user.email 2>/dev/null)"
  if [ -z "$name" ]; then git config user.name "oris-insight-rebuild-bot" >> "$LOG_FILE" 2>&1; fi
  if [ -z "$email" ]; then git config user.email "oris-insight-rebuild-bot@example.local" >> "$LOG_FILE" 2>&1; fi
}

summary "Insight Rebuild Module 14 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_14_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_14_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_14_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_14_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 14 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  cat /tmp/insight_module_14_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_14_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_14*.sh' ! -name 'bootstrap_insight_rebuild_module_14.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_14_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 14 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Module 14 unit tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
if [ "$TEST_RC" -eq 0 ]; then TEST_STATUS="passed"; else TEST_STATUS="failed"; fi
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"

export TEST_RC TEST_STATUS PRODUCT_BASE_SHA TEST_COMMAND VERSION LOG_FILE
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import json
import os
from datetime import datetime, timezone
from pathlib import Path
result = {
    "module": "Insight Rebuild Module 14",
    "bootstrap_version": os.environ.get("VERSION", ""),
    "status": os.environ.get("TEST_STATUS", "failed"),
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "test_command": os.environ.get("TEST_COMMAND", ""),
    "test_exit_code": int(os.environ.get("TEST_RC", "1")),
    "product_base_sha": os.environ.get("PRODUCT_BASE_SHA", ""),
    "managed_database_adapter_boundary": True,
    "default_sqlite_runtime_safe": True,
    "postgres_boundary_adapter": True,
    "credential_redaction": True,
    "migration_preview_only": True,
    "live_connection_attempted": False,
    "adapter_version": "2026-06-24-module-14",
    "expected_unit_test_count": 41,
    "log_file": os.environ.get("LOG_FILE", ""),
    "checks": [
        "prior_module_test_compatibility",
        "default_adapter_disabled_sqlite_safe",
        "postgres_boundary_missing_credential",
        "postgres_boundary_credential_redaction",
        "migration_preview_manifest_only",
        "summary_reports_no_live_connection_attempt",
        "live_flag_read_without_connection_attempt"
    ]
}
Path("reports/testing/insight_rebuild_module_14_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
Path("reports/testing/latest_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
PY

cat > reports/execution/insight_rebuild_module_14_execution_report.md <<EOF
# Insight Rebuild Module 14 Execution Report

## Module

Managed Database Adapter Boundary

## Bootstrap Version

$VERSION

## Product Base Commit

$PRODUCT_BASE_SHA

## Test Command

$TEST_COMMAND

## Test Result

- test exit code: $TEST_RC
- status: $TEST_STATUS
- expected unit test count: 41

## Implemented Boundaries

- managed database adapter settings
- disabled/default adapter for SQLite runtime safety
- PostgreSQL boundary adapter
- migration preview using Module 13 manifest
- adapter readiness summary
- credential presence detection without credential exposure
- no live database connection attempt in Module 14

## Evidence Files

- app/managed_database_adapter.py
- tests/test_module_14_managed_database_adapter.py
- docs/rebuild/INSIGHT_REBUILD_MODULE_14_MANAGED_DATABASE_ADAPTER.md
- docs/testing/INSIGHT_REBUILD_MODULE_14_TEST_PLAN.md
- scripts/bootstrap_insight_rebuild_module_14.sh
- reports/testing/insight_rebuild_module_14_test_result.json
- reports/testing/latest_test_result.json
- reports/execution/insight_rebuild_module_14_bootstrap_latest.log

## Insight Rebuild Module 14 Evidence Commit SHA

Pending until evidence commit completes.

## Next Module

Module 15 should focus on remote Runtime v2 worker queue integration, tenant and billing schema, managed database live smoke in a controlled non-production environment, or provider-backed generation smoke with explicitly configured safe credentials.
EOF

ensure_git_identity
git add reports/testing/insight_rebuild_module_14_test_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_14_execution_report.md reports/execution/insight_rebuild_module_14_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-14): add managed database adapter evidence" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 14 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from pathlib import Path
p = Path("reports/execution/insight_rebuild_module_14_execution_report.md")
text = p.read_text(encoding="utf-8").replace("Pending until evidence commit completes.", "$EVIDENCE_SHA")
p.write_text(text, encoding="utf-8")
PY
git add reports/execution/insight_rebuild_module_14_execution_report.md reports/execution/insight_rebuild_module_14_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-14): record managed database adapter evidence commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$TEST_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 14 tests passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_14_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 14 tests failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_14_execution_report.md"
exit "$TEST_RC"
