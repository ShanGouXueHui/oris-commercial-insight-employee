#!/usr/bin/env bash

# Insight Rebuild Module 9 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-24-insight-rebuild-module-9-official"
WORKDIR="${INSIGHT_WORKDIR:-$HOME/projects}"
PRODUCT_DIR="${PRODUCT_DIR:-$WORKDIR/oris-commercial-insight-employee}"
BRANCH="${INSIGHT_BRANCH:-main}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
HOST="127.0.0.1"
PORT="${ORIS_INSIGHT_SMOKE_PORT:-8099}"
BASE_URL="http://$HOST:$PORT"
LOG_FILE=""
SERVER_PID=""

summary() { printf '%s\n' "$1"; }

cleanup_server() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" >> "$LOG_FILE" 2>&1 || true
    wait "$SERVER_PID" >> "$LOG_FILE" 2>&1 || true
  fi
}

fail_short() {
  cleanup_server
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

summary "Insight Rebuild Module 9 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_9_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_9_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_9_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing reports/evidence/runtime_runs
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_9_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 9 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo "base_url=$BASE_URL"
  echo ""
  cat /tmp/insight_module_9_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_9_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_9*.sh' ! -name 'bootstrap_insight_rebuild_module_9.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_9_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 9 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Module 9 unit tests quietly..."
UNIT_TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
UNIT_TEST_RC=$?

export ORIS_INSIGHT_EVIDENCE_STORAGE="sqlite"
export ORIS_INSIGHT_EVIDENCE_LOCAL_PATH="$PRODUCT_DIR/reports/evidence/runtime_runs/module9_smoke.sqlite3"
export ORIS_INSIGHT_SMOKE_BASE_URL="$BASE_URL"
rm -f "$ORIS_INSIGHT_EVIDENCE_LOCAL_PATH" >> "$LOG_FILE" 2>&1

summary "Starting local uvicorn smoke target..."
$PYTHON_BIN -m uvicorn app.main:app --host "$HOST" --port "$PORT" >> "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo "server_pid=$SERVER_PID" >> "$LOG_FILE"
sleep 1

summary "Running Module 9 HTTP smoke test quietly..."
$PYTHON_BIN scripts/run_module_9_smoke.py >> "$LOG_FILE" 2>&1
SMOKE_RC=$?
cleanup_server
SERVER_PID=""

if [ "$UNIT_TEST_RC" -eq 0 ] && [ "$SMOKE_RC" -eq 0 ]; then TEST_STATUS="passed"; else TEST_STATUS="failed"; fi
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"

export UNIT_TEST_RC SMOKE_RC TEST_STATUS PRODUCT_BASE_SHA UNIT_TEST_COMMAND VERSION LOG_FILE BASE_URL
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import json
import os
from datetime import datetime, timezone
from pathlib import Path
result = {
    "module": "Insight Rebuild Module 9",
    "bootstrap_version": os.environ.get("VERSION", ""),
    "status": os.environ.get("TEST_STATUS", "failed"),
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "unit_test_command": os.environ.get("UNIT_TEST_COMMAND", ""),
    "unit_test_exit_code": int(os.environ.get("UNIT_TEST_RC", "1")),
    "smoke_test_command": "python3 scripts/run_module_9_smoke.py",
    "smoke_test_exit_code": int(os.environ.get("SMOKE_RC", "1")),
    "product_base_sha": os.environ.get("PRODUCT_BASE_SHA", ""),
    "base_url": os.environ.get("BASE_URL", ""),
    "sqlite_path": os.environ.get("ORIS_INSIGHT_EVIDENCE_LOCAL_PATH", ""),
    "deployment_smoke_test": True,
    "runtime_observability": True,
    "sqlite_persistence_smoke": True,
    "expected_unit_test_count": 16,
    "log_file": os.environ.get("LOG_FILE", ""),
    "checks": [
        "unit_tests",
        "uvicorn_startup",
        "healthz",
        "healthz_details",
        "healthz_observability",
        "rebuild_acceptance",
        "rebuild_brief_sqlite_persistence",
        "sqlite_persistence_counts"
    ]
}
Path("reports/testing/insight_rebuild_module_9_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
Path("reports/testing/latest_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
PY

cat > reports/execution/insight_rebuild_module_9_execution_report.md <<EOF
# Insight Rebuild Module 9 Execution Report

## Module

Deployment Smoke Test and Runtime Observability

## Bootstrap Version

$VERSION

## Product Base Commit

$PRODUCT_BASE_SHA

## Unit Test Command

$UNIT_TEST_COMMAND

## Smoke Test Command

python3 scripts/run_module_9_smoke.py

## Test Result

- unit test exit code: $UNIT_TEST_RC
- smoke test exit code: $SMOKE_RC
- status: $TEST_STATUS
- base url: $BASE_URL
- sqlite path: $ORIS_INSIGHT_EVIDENCE_LOCAL_PATH

## Evidence Files

- app/observability.py
- app/main.py
- app/rebuild_api.py
- scripts/run_module_9_smoke.py
- tests/test_module_9_observability.py
- docs/rebuild/INSIGHT_REBUILD_MODULE_9_DEPLOYMENT_SMOKE_AND_OBSERVABILITY.md
- docs/testing/INSIGHT_REBUILD_MODULE_9_TEST_PLAN.md
- scripts/bootstrap_insight_rebuild_module_9.sh
- reports/testing/insight_rebuild_module_9_test_result.json
- reports/testing/insight_rebuild_module_9_smoke_result.json
- reports/testing/latest_test_result.json
- reports/execution/insight_rebuild_module_9_bootstrap_latest.log

## Insight Rebuild Module 9 Evidence Commit SHA

Pending until evidence commit completes.

## Next Module

Module 10 should focus on authenticated provider/source adapter integration or commercial guardrails such as auth, quota, rate limits, and error policy.
EOF

ensure_git_identity
git add reports/testing/insight_rebuild_module_9_test_result.json reports/testing/insight_rebuild_module_9_smoke_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_9_execution_report.md reports/execution/insight_rebuild_module_9_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-9): add smoke evidence reports" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 9 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from pathlib import Path
p = Path("reports/execution/insight_rebuild_module_9_execution_report.md")
text = p.read_text(encoding="utf-8").replace("Pending until evidence commit completes.", "$EVIDENCE_SHA")
p.write_text(text, encoding="utf-8")
PY
git add reports/execution/insight_rebuild_module_9_execution_report.md reports/execution/insight_rebuild_module_9_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-9): record smoke evidence commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$UNIT_TEST_RC" -eq 0 ] && [ "$SMOKE_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 9 smoke passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_9_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 9 smoke failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_9_execution_report.md"
exit 1
