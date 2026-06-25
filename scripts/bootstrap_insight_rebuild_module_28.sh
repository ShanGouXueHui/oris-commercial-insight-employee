#!/usr/bin/env bash

# Insight Rebuild Module 28 official bootstrap script.
# Do not use set -e.

VERSION="2026-06-25-insight-rebuild-module-28-official"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PRODUCT_DIR="${PRODUCT_DIR:-$HOME/projects/oris-commercial-insight-employee}"
BRANCH="${INSIGHT_BRANCH:-main}"
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_28_bootstrap_latest.log"

printf '%s\n' "Insight Rebuild Module 28 official bootstrap $VERSION starting..."
cd "$PRODUCT_DIR" || exit 1
git fetch origin >/tmp/insight_module_28_git.log 2>&1
git checkout "$BRANCH" >>/tmp/insight_module_28_git.log 2>&1
git pull --ff-only origin "$BRANCH" >>/tmp/insight_module_28_git.log 2>&1
mkdir -p reports/testing reports/execution
cat /tmp/insight_module_28_git.log > "$LOG_FILE" 2>/dev/null
rm -f /tmp/insight_module_28_git.log
printf '%s\n' "Running Module 28 unit tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p test_*.py -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
export VERSION TEST_COMMAND TEST_RC PRODUCT_BASE_SHA LOG_FILE
$PYTHON_BIN scripts/module_28_evidence_writer.py >> "$LOG_FILE" 2>&1
git add reports/testing reports/execution >> "$LOG_FILE" 2>&1
git commit -m "insight-rebuild(module-28): add evidence" >> "$LOG_FILE" 2>&1
git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
if [ "$TEST_RC" -eq 0 ]; then
  printf '%s\n' "DONE: Insight Rebuild Module 28 tests passed. Evidence pushed."
else
  printf '%s\n' "FAILED: Insight Rebuild Module 28 tests failed. Evidence pushed."
fi
printf '%s\n' "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_28_execution_report.md"
exit "$TEST_RC"
