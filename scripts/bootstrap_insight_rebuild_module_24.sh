#!/usr/bin/env bash

# Insight Rebuild Module 24 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-25-insight-rebuild-module-24-official"
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

summary "Insight Rebuild Module 24 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_24_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_24_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_24_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_24_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 24 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  cat /tmp/insight_module_24_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_24_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_24*.sh' ! -name 'bootstrap_insight_rebuild_module_24.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_24_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 24 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Module 24 unit tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"

export TEST_RC PRODUCT_BASE_SHA TEST_COMMAND VERSION LOG_FILE
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import os
from app.evidence_harness import EvidenceHarnessConfig, TestRunSnapshot, write_harness_evidence
config = EvidenceHarnessConfig(
    module_name="Insight Rebuild Module 24",
    bootstrap_version=os.environ.get("VERSION", ""),
    expected_unit_test_count=137,
    result_filename="insight_rebuild_module_24_test_result.json",
    report_filename="insight_rebuild_module_24_execution_report.md",
    implemented_boundaries=(
        "monthly period helper",
        "tenant usage ledger protocol",
        "tenant usage snapshot contract",
        "in-memory tenant usage ledger",
        "default tenant usage ledger reset helper",
        "entitlement evaluation against ledger usage",
        "tenant usage ledger summary",
        "request path unchanged in Module 24",
    ),
    evidence_files=(
        "app/tenant_usage_ledger.py",
        "tests/test_module_24_tenant_usage_ledger.py",
        "docs/product/TENANT_USAGE_LEDGER_GUIDE.md",
        "docs/rebuild/INSIGHT_REBUILD_MODULE_24_TENANT_USAGE_LEDGER.md",
        "docs/testing/INSIGHT_REBUILD_MODULE_24_TEST_PLAN.md",
        "scripts/bootstrap_insight_rebuild_module_24.sh",
        "reports/testing/insight_rebuild_module_24_test_result.json",
        "reports/testing/latest_test_result.json",
        "reports/execution/insight_rebuild_module_24_bootstrap_latest.log",
    ),
    next_module="Module 25 should connect the tenant usage ledger to tenant middleware behind explicit configuration, or migrate another bootstrap script to app.evidence_harness.",
)
snapshot = TestRunSnapshot(
    test_command=os.environ.get("TEST_COMMAND", ""),
    test_exit_code=int(os.environ.get("TEST_RC", "1")),
    product_base_sha=os.environ.get("PRODUCT_BASE_SHA", ""),
    log_file=os.environ.get("LOG_FILE", ""),
)
write_harness_evidence(
    config,
    snapshot,
    flags={
        "tenant_usage_ledger": True,
        "tenant_usage_ledger_type": "in_memory",
        "monthly_period_supported": True,
        "consume_supported": True,
        "snapshot_supported": True,
        "request_path_unchanged": True,
        "tenant_usage_ledger_version": "2026-06-25-module-24",
    },
    checks=(
        "prior_module_test_compatibility",
        "monthly_period_deterministic",
        "empty_ledger_returns_zero_usage",
        "consume_increments_monthly_usage",
        "snapshot_reports_current_count",
        "entitlement_evaluation_uses_ledger_usage",
        "entitlement_evaluation_blocks_at_quota",
        "summary_reports_local_only_ledger",
    ),
)
PY

ensure_git_identity
git add reports/testing/insight_rebuild_module_24_test_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_24_execution_report.md reports/execution/insight_rebuild_module_24_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-24): add tenant usage ledger evidence" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 24 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from app.evidence_harness import record_evidence_commit_sha
record_evidence_commit_sha("reports/execution/insight_rebuild_module_24_execution_report.md", "$EVIDENCE_SHA")
PY
git add reports/execution/insight_rebuild_module_24_execution_report.md reports/execution/insight_rebuild_module_24_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-24): record tenant usage ledger evidence commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$TEST_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 24 tests passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_24_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 24 tests failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_24_execution_report.md"
exit "$TEST_RC"
