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
state="reports/ota/last_instruction_seq.txt"
{
  echo "timestamp: $ts"
  echo "entry: unified-OTA-entry.sh"
  echo "instruction: ops/ota/next_instruction.json"
  git pull --ff-only origin main
  seq="$(python3 -c "import json; print(json.load(open('ops/ota/next_instruction.json')).get('instruction_seq',''))")"
  last=""
  if [ -f "$state" ]; then last="$(cat "$state")"; fi
  echo "instruction_seq: $seq"
  echo "last_instruction_seq: $last"
  if [ -n "$seq" ] && [ "$seq" = "$last" ]; then
    echo "no new instruction"
    exit 0
  fi
  python3 -m unittest discover -s tests -p 'test_*.py' -q
  TEST_RC=$?
  export TEST_RC
  python3 scripts/w70.py
  if [ "$TEST_RC" = "0" ]; then echo "$seq" > "$state"; fi
  git add reports/testing reports/execution reports/ota "$log" "$state"
  git commit -m "Add OTA execution evidence" || true
  git push origin main || true
  exit "$TEST_RC"
} 2>&1 | tee "$log"
exit "${PIPESTATUS[0]}"
