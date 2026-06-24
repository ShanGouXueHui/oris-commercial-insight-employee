#!/usr/bin/env bash

# Insight Rebuild Module 8 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-24-insight-rebuild-module-8-official"
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

summary "Insight Rebuild Module 8 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_8_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_8_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_8_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_8_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 8 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  cat /tmp/insight_module_8_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_8_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_8*.sh' ! -name 'bootstrap_insight_rebuild_module_8.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_8_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 8 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Insight Rebuild Module 8 acceptance tests quietly..."
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
    "module": "Insight Rebuild Module 8",
    "bootstrap_version": os.environ.get("VERSION", ""),
    "status": os.environ.get("TEST_STATUS", "failed"),
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "test_command": os.environ.get("TEST_COMMAND", ""),
    "test_exit_code": int(os.environ.get("TEST_RC", "1")),
    "product_base_sha": os.environ.get("PRODUCT_BASE_SHA", ""),
    "durable_evidence_persistence": True,
    "sqlite_schema_version": "2026-06-24-module-8",
    "sqlite_tables": ["persistence_metadata", "runtime_runs", "evidence_sources", "evidence_items"],
    "runtime_adapter_sqlite_persistence": True,
    "log_file": os.environ.get("LOG_FILE", ""),
    "checks": [
        "api_surface_compatibility",
        "module_7_orchestration_compatibility",
        "sqlite_schema_initialization",
        "sqlite_source_and_evidence_persistence",
        "config_driven_sqlite_store_selection",
        "runtime_adapter_sqlite_persistence"
    ]
}
Path("reports/testing/insight_rebuild_module_8_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
Path("reports/testing/latest_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
PY

cat > reports/execution/insight_rebuild_module_8_execution_report.md <<EOF
# Insight Rebuild Module 8 Execution Report

## Module

Durable Evidence Persistence and Database Schema

## Bootstrap Version

$VERSION

## Product Base Commit

$PRODUCT_BASE_SHA

## Test Command

$TEST_COMMAND

## Test Result

- test exit code: $TEST_RC
- status: $TEST_STATUS

## Evidence Files

- app/config.py
- app/evidence_persistence.py
- app/rebuild_api.py
- tests/test_module_8_durable_persistence.py
- docs/rebuild/INSIGHT_REBUILD_MODULE_8_DURABLE_EVIDENCE_PERSISTENCE.md
- docs/testing/INSIGHT_REBUILD_MODULE_8_TEST_PLAN.md
- scripts/bootstrap_insight_rebuild_module_8.sh
- reports/testing/insight_rebuild_module_8_test_result.json
- reports/testing/latest_test_result.json
- reports/execution/insight_rebuild_module_8_bootstrap_latest.log

## Insight Rebuild Module 8 Evidence Commit SHA

Pending until evidence commit completes.

## Next Module

Module 9 should focus on deployment smoke testing and runtime observability, or on authenticated external provider integration behind the Module 7 and Module 8 boundaries.
EOF

ensure_git_identity
git add reports/testing/insight_rebuild_module_8_test_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_8_execution_report.md reports/execution/insight_rebuild_module_8_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-8): add acceptance evidence reports" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 8 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from pathlib import Path
p = Path("reports/execution/insight_rebuild_module_8_execution_report.md")
text = p.read_text(encoding="utf-8").replace("Pending until evidence commit completes.", "$EVIDENCE_SHA")
p.write_text(text, encoding="utf-8")
PY
git add reports/execution/insight_rebuild_module_8_execution_report.md reports/execution/insight_rebuild_module_8_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-8): record evidence commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$TEST_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 8 tests passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_8_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 8 tests failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_8_execution_report.md"
exit "$TEST_RC"
