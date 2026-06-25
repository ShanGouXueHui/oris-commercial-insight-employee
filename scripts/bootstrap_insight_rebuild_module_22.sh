#!/usr/bin/env bash

# Insight Rebuild Module 22 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-25-insight-rebuild-module-22-official"
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

summary "Insight Rebuild Module 22 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_22_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_22_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_22_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_22_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 22 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  cat /tmp/insight_module_22_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_22_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_22*.sh' ! -name 'bootstrap_insight_rebuild_module_22.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_22_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 22 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Module 22 unit tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"

export TEST_RC PRODUCT_BASE_SHA TEST_COMMAND VERSION LOG_FILE
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import os
from app.evidence_harness import EvidenceHarnessConfig, TestRunSnapshot, write_harness_evidence
config = EvidenceHarnessConfig(
    module_name="Insight Rebuild Module 22",
    bootstrap_version=os.environ.get("VERSION", ""),
    expected_unit_test_count=122,
    result_filename="insight_rebuild_module_22_test_result.json",
    report_filename="insight_rebuild_module_22_execution_report.md",
    implemented_boundaries=(
        "tenant guardrail policy contract",
        "tenant guardrail decision contract",
        "tenant ID extraction from headers",
        "commercial guardrail short-circuit behavior",
        "exempt-path entitlement skipping",
        "entitlement observe mode",
        "entitlement blocking mode",
        "missing entitlement block",
        "monthly quota exhaustion block",
        "local provider-free summary",
        "no production middleware behavior change in Module 22",
    ),
    evidence_files=(
        "app/tenant_guardrails.py",
        "tests/test_module_22_tenant_guardrails.py",
        "docs/product/TENANT_GUARDRAIL_BRIDGE_GUIDE.md",
        "docs/rebuild/INSIGHT_REBUILD_MODULE_22_TENANT_GUARDRAILS.md",
        "docs/testing/INSIGHT_REBUILD_MODULE_22_TEST_PLAN.md",
        "scripts/bootstrap_insight_rebuild_module_22.sh",
        "reports/testing/insight_rebuild_module_22_test_result.json",
        "reports/testing/latest_test_result.json",
        "reports/execution/insight_rebuild_module_22_bootstrap_latest.log",
    ),
    next_module="Module 23 should activate the tenant guardrail bridge in API middleware behind explicit configuration, or continue selective bootstrap migration to app.evidence_harness.",
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
        "tenant_guardrail_bridge": True,
        "commercial_guardrail_bridge": True,
        "tenant_entitlement_bridge": True,
        "billing_provider_integrated": False,
        "payment_processing_enabled": False,
        "production_middleware_changed": False,
        "local_deterministic_only": True,
        "tenant_guardrail_version": "2026-06-25-module-22",
    },
    checks=(
        "prior_module_test_compatibility",
        "observe_mode_reports_missing_entitlement_non_blocking",
        "blocking_mode_blocks_missing_entitlement",
        "blocking_mode_blocks_monthly_quota_exceeded",
        "blocking_mode_allows_valid_entitlement_under_quota",
        "commercial_guardrail_block_short_circuits_entitlement",
        "exempt_path_skips_entitlement",
        "summary_reports_provider_free_local_behavior",
    ),
)
PY

ensure_git_identity
git add reports/testing/insight_rebuild_module_22_test_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_22_execution_report.md reports/execution/insight_rebuild_module_22_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-22): add tenant guardrail evidence" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 22 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from app.evidence_harness import record_evidence_commit_sha
record_evidence_commit_sha("reports/execution/insight_rebuild_module_22_execution_report.md", "$EVIDENCE_SHA")
PY
git add reports/execution/insight_rebuild_module_22_execution_report.md reports/execution/insight_rebuild_module_22_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-22): record tenant guardrail evidence commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$TEST_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 22 tests passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_22_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 22 tests failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_22_execution_report.md"
exit "$TEST_RC"
