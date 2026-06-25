#!/usr/bin/env bash

# Insight Rebuild Module 20 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-25-insight-rebuild-module-20-official"
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

summary "Insight Rebuild Module 20 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_20_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_20_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_20_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_20_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 20 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  cat /tmp/insight_module_20_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_20_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_20*.sh' ! -name 'bootstrap_insight_rebuild_module_20.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_20_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 20 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Module 20 unit tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"

export TEST_RC PRODUCT_BASE_SHA TEST_COMMAND VERSION LOG_FILE
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import os
from app.evidence_harness import EvidenceHarnessConfig, TestRunSnapshot, write_harness_evidence
config = EvidenceHarnessConfig(
    module_name="Insight Rebuild Module 20",
    bootstrap_version=os.environ.get("VERSION", ""),
    expected_unit_test_count=84,
    result_filename="insight_rebuild_module_20_test_result.json",
    report_filename="insight_rebuild_module_20_execution_report.md",
    implemented_boundaries=(
        "evidence harness config contract",
        "test run snapshot contract",
        "latest-test-result payload builder",
        "execution report renderer",
        "evidence file writer",
        "evidence commit SHA recorder",
        "sensitive value redaction",
        "reusable bootstrap helper",
    ),
    evidence_files=(
        "app/evidence_harness.py",
        "tests/test_module_20_evidence_harness.py",
        "docs/product/EVIDENCE_HARNESS_HELPER_GUIDE.md",
        "docs/rebuild/INSIGHT_REBUILD_MODULE_20_EVIDENCE_HARNESS.md",
        "docs/testing/INSIGHT_REBUILD_MODULE_20_TEST_PLAN.md",
        "scripts/bootstrap_insight_rebuild_module_20.sh",
        "reports/testing/insight_rebuild_module_20_test_result.json",
        "reports/testing/latest_test_result.json",
        "reports/execution/insight_rebuild_module_20_bootstrap_latest.log",
    ),
    next_module="Module 21 should migrate selected older bootstrap scripts to the reusable evidence harness helper, or integrate tenant entitlements into commercial guardrails.",
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
        "evidence_harness_helper": True,
        "latest_result_writer": True,
        "execution_report_renderer": True,
        "sensitive_value_redaction": True,
        "evidence_commit_recorder": True,
        "reusable_bootstrap_helper": True,
        "live_external_action_enabled": False,
    },
    checks=(
        "prior_module_test_compatibility",
        "snapshot_status_from_exit_code",
        "latest_result_payload_required_fields",
        "sensitive_values_redacted",
        "execution_report_rendering",
        "harness_writer_outputs_files",
        "evidence_commit_sha_recorder",
        "summary_reports_helper_flags",
    ),
)
PY

ensure_git_identity
git add reports/testing/insight_rebuild_module_20_test_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_20_execution_report.md reports/execution/insight_rebuild_module_20_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-20): add evidence harness evidence" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 20 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from app.evidence_harness import record_evidence_commit_sha
record_evidence_commit_sha("reports/execution/insight_rebuild_module_20_execution_report.md", "$EVIDENCE_SHA")
PY
git add reports/execution/insight_rebuild_module_20_execution_report.md reports/execution/insight_rebuild_module_20_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-20): record evidence harness commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$TEST_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 20 tests passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_20_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 20 tests failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_20_execution_report.md"
exit "$TEST_RC"
