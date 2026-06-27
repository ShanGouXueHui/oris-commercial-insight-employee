#!/usr/bin/env bash
ROOT="${PRODUCT_DIR:-$HOME/projects/oris-commercial-insight-employee}"
cd "$ROOT" || exit 1
LOCK="/tmp/oris-unified-ota.lock"
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "unified ota already running"
  exit 0
fi
trap 'rmdir "$LOCK"' EXIT
mkdir -p reports/ota
ts="$(date -u +%Y%m%dT%H%M%SZ)"
log="reports/ota/unified_ota_${ts}.log"
{
  echo "timestamp: $ts"
  echo "entry: unified-OTA-entry.sh"
  echo "instruction: ops/ota/next_instruction.json"
  git pull --ff-only origin main
  python3 -m unittest discover -s tests -p 'test_*.py' -q
  TEST_RC=$?
  export TEST_RC
  python3 scripts/w70.py
  git add reports/testing/latest_test_result.json reports/testing/insight_rebuild_module_70_test_result.json reports/execution/insight_rebuild_module_70_execution_report.md reports/ota "$log"
  git commit -m "Add module 70 execution evidence" || true
  git push origin main || true
  exit "$TEST_RC"
} 2>&1 | tee "$log"
exit "${PIPESTATUS[0]}"
