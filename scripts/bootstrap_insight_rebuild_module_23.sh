#!/usr/bin/env bash

# Insight Rebuild Module 23 official bootstrap script.
# Policy: do not use set -e; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-25-insight-rebuild-module-23-official"
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

summary "Insight Rebuild Module 23 official bootstrap $VERSION starting..."
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
git fetch origin >/tmp/insight_module_23_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_23_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_23_git.log 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi

mkdir -p reports/execution reports/testing
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_23_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 23 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  cat /tmp/insight_module_23_git.log 2>/dev/null || true
} > "$LOG_FILE" 2>&1
rm -f /tmp/insight_module_23_git.log

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_23*.sh' ! -name 'bootstrap_insight_rebuild_module_23.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_23_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 23 bootstrap entrypoints found; keep one official entry only"
fi

summary "Running Module 23 unit tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"

export TEST_RC PRODUCT_BASE_SHA TEST_COMMAND VERSION LOG_FILE
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import os
from app.evidence_harness import EvidenceHarnessConfig, TestRunSnapshot, write_harness_evidence
config = EvidenceHarnessConfig(
    module_name="Insight Rebuild Module 23",
    bootstrap_version=os.environ.get("VERSION", ""),
    expected_unit_test_count=130,
    result_filename="insight_rebuild_module_23_test_result.json",
    report_filename="insight_rebuild_module_23_execution_report.md",
    implemented_boundaries=(
        "tenant guardrail settings in product configuration",
        "explicit tenant guardrail activation flag",
        "local deterministic tenant entitlement settings",
        "tenant guardrail policy adapter from settings",
        "local entitlement builder from settings",
        "middleware branch for tenant guardrail evaluation",
        "tenant guardrail response headers",
        "health details tenant settings visibility",
        "existing commercial guardrail behavior preserved by default",
    ),
    evidence_files=(
        "app/config.py",
        "app/main.py",
        "app/tenant_guardrails.py",
        "tests/test_module_23_tenant_middleware.py",
        "docs/product/TENANT_GUARDRAIL_MIDDLEWARE_GUIDE.md",
        "docs/rebuild/INSIGHT_REBUILD_MODULE_23_TENANT_MIDDLEWARE.md",
        "docs/testing/INSIGHT_REBUILD_MODULE_23_TEST_PLAN.md",
        "scripts/bootstrap_insight_rebuild_module_23.sh",
        "reports/testing/insight_rebuild_module_23_test_result.json",
        "reports/testing/latest_test_result.json",
        "reports/execution/insight_rebuild_module_23_bootstrap_latest.log",
    ),
    next_module="Module 24 should focus on a local tenant entitlement usage ledger, or selectively migrate another bootstrap script to app.evidence_harness.",
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
        "tenant_middleware_activation": True,
        "tenant_guardrails_default_enabled": False,
        "explicit_activation_required": True,
        "local_entitlements_only": True,
        "existing_commercial_guardrail_default_preserved": True,
        "live_external_action_enabled": False,
        "tenant_middleware_version": "2026-06-25-module-23",
    },
    checks=(
        "prior_module_test_compatibility",
        "default_tenant_guardrails_disabled",
        "disabled_path_preserves_existing_headers",
        "enabled_observe_mode_adds_tenant_headers",
        "enabled_blocking_mode_blocks_missing_entitlement",
        "enabled_blocking_mode_allows_configured_local_entitlement",
        "health_details_reports_tenant_guardrail_settings",
        "local_entitlement_builder_uses_configured_plan",
        "activation_summary_reports_default_behavior_change",
    ),
)
PY

ensure_git_identity
git add reports/testing/insight_rebuild_module_23_test_result.json reports/testing/latest_test_result.json reports/execution/insight_rebuild_module_23_execution_report.md reports/execution/insight_rebuild_module_23_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-23): add tenant middleware evidence" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "git commit failed for Module 23 evidence"; fi
EVIDENCE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
"$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from app.evidence_harness import record_evidence_commit_sha
record_evidence_commit_sha("reports/execution/insight_rebuild_module_23_execution_report.md", "$EVIDENCE_SHA")
PY
git add reports/execution/insight_rebuild_module_23_execution_report.md reports/execution/insight_rebuild_module_23_bootstrap_latest.log >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-23): record tenant middleware evidence commit sha" >> "$LOG_FILE" 2>&1
FINAL_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
rc=$?
if [ "$rc" -ne 0 ]; then fail_short "local evidence committed but push failed; local commit $FINAL_SHA"; fi

if [ "$TEST_RC" -eq 0 ]; then
  summary "DONE: Insight Rebuild Module 23 tests passed. Evidence pushed."
  summary "Commit: $FINAL_SHA"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_23_execution_report.md"
  exit 0
fi
summary "FAILED: Insight Rebuild Module 23 tests failed. Evidence pushed."
summary "Commit: $FINAL_SHA"
summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_23_execution_report.md"
exit "$TEST_RC"
