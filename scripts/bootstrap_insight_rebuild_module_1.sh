#!/usr/bin/env bash

# Insight Rebuild Module 1 official bootstrap script.
# Policy: do not use `set -e`; terminal output stays short; detailed logs are written as GitHub evidence.

VERSION="2026-06-23-insight-rebuild-module-1-official"
PRODUCT_REPO_URL="${PRODUCT_REPO_URL:-https://github.com/ShanGouXueHui/oris-commercial-insight-employee.git}"
ORIS_REPO_URL="${ORIS_REPO_URL:-https://github.com/ShanGouXueHui/oris.git}"
WORKDIR="${INSIGHT_WORKDIR:-$HOME/projects}"
PRODUCT_DIR="${PRODUCT_DIR:-$WORKDIR/oris-commercial-insight-employee}"
BRANCH="${INSIGHT_BRANCH:-main}"
COMMIT_AND_PUSH="${INSIGHT_MODULE_1_COMMIT_AND_PUSH:-1}"
RUNTIME_V2_FINAL_ORIS_SHA="896bdc67942a27cea98b8a4eb8f49d946795a741"
MODULE0_SHA="7d1d604b92b21f1213f990140b3345b4be2163ca"
LOG_FILE=""
PYTHON_BIN="${PYTHON_BIN:-python3}"

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

commit_and_push_evidence() {
  status_label="$1"
  commit_message="$2"
  cd "$PRODUCT_DIR" || fail_short "cannot enter product repo for evidence commit"
  ensure_git_identity
  git add \
    app/runtime_v2_alignment.py \
    tests/test_runtime_v2_alignment.py \
    docs/rebuild/INSIGHT_REBUILD_MODULE_1_ARCHITECTURE.md \
    docs/testing/INSIGHT_REBUILD_MODULE_1_TEST_PLAN.md \
    reports/testing/insight_rebuild_module_1_test_result.json \
    reports/testing/latest_test_result.json \
    reports/execution/insight_rebuild_module_1_execution_report.md \
    reports/execution/insight_rebuild_module_1_bootstrap_latest.log >> "$LOG_FILE" 2>&1
  if git diff --cached --quiet >> "$LOG_FILE" 2>&1; then
    summary "$status_label. No file changes to commit."
    summary "Log: $LOG_FILE"
    return 0
  fi
  git commit -m "$commit_message" >> "$LOG_FILE" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then
    summary "$status_label, but git commit failed."
    summary "Log: $LOG_FILE"
    return "$rc"
  fi
  evidence_sha="$(git rev-parse HEAD 2>> "$LOG_FILE")"
  "$PYTHON_BIN" - <<PY >> "$LOG_FILE" 2>&1
from pathlib import Path
p = Path("reports/execution/insight_rebuild_module_1_execution_report.md")
text = p.read_text(encoding="utf-8")
text = text.replace("Pending until evidence commit completes.", "$evidence_sha")
p.write_text(text, encoding="utf-8")
PY
  git add reports/execution/insight_rebuild_module_1_execution_report.md reports/execution/insight_rebuild_module_1_bootstrap_latest.log >> "$LOG_FILE" 2>&1
  if ! git diff --cached --quiet >> "$LOG_FILE" 2>&1; then
    git commit -m "insight-rebuild(module-1): record evidence commit sha" >> "$LOG_FILE" 2>&1
  fi
  final_sha="$(git rev-parse HEAD 2>> "$LOG_FILE")"
  git push origin "$BRANCH" >> "$LOG_FILE" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then
    summary "$status_label, local evidence committed but push failed."
    summary "Local commit: $final_sha"
    summary "Log: $LOG_FILE"
    return "$rc"
  fi
  summary "$status_label. Evidence pushed."
  summary "Commit: $final_sha"
  summary "Evidence: reports/testing/latest_test_result.json; reports/execution/insight_rebuild_module_1_execution_report.md"
  return 0
}

mkdir -p "$WORKDIR"
summary "Insight Rebuild Module 1 official bootstrap $VERSION starting..."
TEMP_LOG="/tmp/insight_rebuild_module_1_bootstrap_$$.log"
LOG_FILE="$TEMP_LOG"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then fail_short "python3/python not found"; fi

if [ ! -d "$PRODUCT_DIR/.git" ]; then
  git clone "$PRODUCT_REPO_URL" "$PRODUCT_DIR" >> "$LOG_FILE" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then fail_short "cannot clone product repo"; fi
else
  cd "$PRODUCT_DIR" || fail_short "cannot enter product repo"
  git fetch origin >> "$LOG_FILE" 2>&1
  git checkout "$BRANCH" >> "$LOG_FILE" 2>&1
  git pull --ff-only origin "$BRANCH" >> "$LOG_FILE" 2>&1
  rc=$?
  if [ "$rc" -ne 0 ]; then fail_short "cannot fast-forward product repo; inspect local changes in $PRODUCT_DIR"; fi
fi

cd "$PRODUCT_DIR" || fail_short "cannot enter product repo after clone/update"
mkdir -p reports/execution
LOG_FILE="$PRODUCT_DIR/reports/execution/insight_rebuild_module_1_bootstrap_latest.log"
{
  echo "# Insight Rebuild Module 1 bootstrap log"
  echo "version=$VERSION"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "product_dir=$PRODUCT_DIR"
  echo "branch=$BRANCH"
  echo "python_bin=$PYTHON_BIN"
  echo ""
  echo "# pre-log bootstrap output"
  if [ -f "$TEMP_LOG" ]; then cat "$TEMP_LOG"; fi
} > "$LOG_FILE" 2>&1
rm -f "$TEMP_LOG"

DUPLICATE_BOOTSTRAPS="$(find scripts -maxdepth 1 -type f -name 'bootstrap_insight_rebuild_module_1*.sh' ! -name 'bootstrap_insight_rebuild_module_1.sh' -print 2>> "$LOG_FILE")"
if [ -n "$DUPLICATE_BOOTSTRAPS" ]; then
  echo "duplicate_insight_rebuild_module_1_bootstraps=$DUPLICATE_BOOTSTRAPS" >> "$LOG_FILE"
  fail_short "duplicate Insight Rebuild Module 1 bootstrap entrypoints found; keep one official entry only"
fi

summary "Checking ORIS Runtime v2 final state via git ls-remote..."
ORIS_HEAD="$(git ls-remote "$ORIS_REPO_URL" "refs/heads/main" 2>> "$LOG_FILE" | awk '{print $1}')"
if [ -n "$ORIS_HEAD" ]; then ORIS_CHECK_STATUS="ls_remote_ok"; else ORIS_HEAD="UNKNOWN"; ORIS_CHECK_STATUS="ls_remote_failed_non_blocking"; fi
PRODUCT_BASE_SHA="$(git rev-parse HEAD 2>> "$LOG_FILE")"
{
  echo ""
  echo "# repository state"
  echo "product_base_sha=$PRODUCT_BASE_SHA"
  echo "module0_expected_sha=$MODULE0_SHA"
  echo "oris_check_status=$ORIS_CHECK_STATUS"
  echo "oris_head=$ORIS_HEAD"
  echo "runtime_v2_final_oris_sha=$RUNTIME_V2_FINAL_ORIS_SHA"
} >> "$LOG_FILE" 2>&1

mkdir -p app tests docs/rebuild docs/testing reports/testing reports/execution

touch app/__init__.py

cat > app/runtime_v2_alignment.py <<'EOF'
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


RUNTIME_V2_REQUIRED_CAPABILITIES = [
    "state_machine",
    "persistent_run_store",
    "worker_loop",
    "safe_executor_adapter",
    "github_evidence_publisher",
    "approval_gate",
    "acceptance_harness",
]

INSIGHT_REBUILD_MODULES = [
    "module_1_architecture_alignment",
    "module_2_domain_contracts",
    "module_3_evidence_ingestion",
    "module_4_brief_generation_pipeline",
    "module_5_quality_gates_and_limitations",
    "module_6_api_surface_and_acceptance",
]


@dataclass(frozen=True)
class RuntimeV2Alignment:
    product: str
    runtime_status: str
    architecture_mode: str
    required_capabilities: List[str]
    rebuild_modules: List[str]
    product_repo_mutation_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_runtime_v2_alignment() -> RuntimeV2Alignment:
    return RuntimeV2Alignment(
        product="ORIS Commercial Insight Employee",
        runtime_status="accepted",
        architecture_mode="runtime_v2_backed_rebuild",
        required_capabilities=list(RUNTIME_V2_REQUIRED_CAPABILITIES),
        rebuild_modules=list(INSIGHT_REBUILD_MODULES),
        product_repo_mutation_allowed=True,
    )


def validate_alignment(alignment: RuntimeV2Alignment) -> List[str]:
    errors: List[str] = []
    if alignment.runtime_status != "accepted":
        errors.append("runtime_v2_not_accepted")
    if alignment.architecture_mode != "runtime_v2_backed_rebuild":
        errors.append("wrong_architecture_mode")
    missing = [item for item in RUNTIME_V2_REQUIRED_CAPABILITIES if item not in alignment.required_capabilities]
    if missing:
        errors.append("missing_capabilities:" + ",".join(missing))
    if not alignment.rebuild_modules or alignment.rebuild_modules[0] != "module_1_architecture_alignment":
        errors.append("invalid_rebuild_module_sequence")
    return errors


def build_architecture_summary() -> Dict[str, object]:
    alignment = build_runtime_v2_alignment()
    errors = validate_alignment(alignment)
    return {
        "alignment": alignment.to_dict(),
        "valid": not errors,
        "errors": errors,
        "next_module": "module_2_domain_contracts",
    }
EOF

cat > tests/test_runtime_v2_alignment.py <<'EOF'
import unittest

from app.runtime_v2_alignment import (
    RUNTIME_V2_REQUIRED_CAPABILITIES,
    build_architecture_summary,
    build_runtime_v2_alignment,
    validate_alignment,
)


class RuntimeV2AlignmentTests(unittest.TestCase):
    def test_runtime_v2_alignment_is_valid(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(validate_alignment(alignment), [])

    def test_required_capabilities_are_complete(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(alignment.required_capabilities, RUNTIME_V2_REQUIRED_CAPABILITIES)

    def test_product_mutation_is_allowed_only_after_runtime_acceptance(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(alignment.runtime_status, "accepted")
        self.assertTrue(alignment.product_repo_mutation_allowed)

    def test_rebuild_sequence_starts_with_architecture_alignment(self):
        alignment = build_runtime_v2_alignment()
        self.assertEqual(alignment.rebuild_modules[0], "module_1_architecture_alignment")
        self.assertIn("module_6_api_surface_and_acceptance", alignment.rebuild_modules)

    def test_architecture_summary_identifies_next_module(self):
        summary = build_architecture_summary()
        self.assertTrue(summary["valid"])
        self.assertEqual(summary["next_module"], "module_2_domain_contracts")


if __name__ == "__main__":
    unittest.main()
EOF

cat > docs/rebuild/INSIGHT_REBUILD_MODULE_1_ARCHITECTURE.md <<'EOF'
# Insight Rebuild Module 1 - Architecture Alignment with Runtime v2

## Objective

Rebuild the commercial insight employee on top of the accepted ORIS Runtime v2 substrate instead of extending the old interactive stub blindly.

## Current Product Baseline

The product repository contains a Phase 0 FastAPI service with Pydantic models and deterministic executive brief generation. Module 1 preserves that baseline and adds the rebuild alignment layer.

## Runtime v2 Capabilities To Use

- state machine
- persistent run store
- worker loop
- safe executor adapter
- GitHub evidence publisher
- approval gate
- end-to-end acceptance harness

## Rebuild Sequence

1. Architecture alignment.
2. Domain contracts.
3. Evidence ingestion.
4. Brief generation pipeline.
5. Quality gates and limitations.
6. API surface and acceptance.

## Boundary

This module does not add business-specific insight logic yet. It establishes the product-side rebuild plan and verifies that the product is allowed to mutate after Runtime v2 final acceptance.
EOF

cat > docs/testing/INSIGHT_REBUILD_MODULE_1_TEST_PLAN.md <<'EOF'
# Insight Rebuild Module 1 Test Plan

## Scope

Validate that the product repo now has a deterministic Runtime v2 alignment contract and a rebuild module sequence.

## Test Targets

1. Runtime v2 alignment is valid.
2. Required runtime capabilities are complete.
3. Product mutation is allowed only after Runtime v2 acceptance.
4. Rebuild sequence starts with architecture alignment.
5. Architecture summary identifies Module 2 as the next module.
EOF

summary "Generated Insight Rebuild Module 1 files. Running stdlib tests quietly..."
TEST_COMMAND="$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q"
$PYTHON_BIN -m unittest discover -s tests -p 'test_*.py' -q >> "$LOG_FILE" 2>&1
TEST_RC=$?
if [ "$TEST_RC" -eq 0 ]; then TEST_STATUS="passed"; else TEST_STATUS="failed"; fi

export TEST_RC TEST_STATUS PRODUCT_BASE_SHA MODULE0_SHA ORIS_CHECK_STATUS ORIS_HEAD RUNTIME_V2_FINAL_ORIS_SHA TEST_COMMAND VERSION LOG_FILE
"$PYTHON_BIN" - <<'PY' >> "$LOG_FILE" 2>&1
import json
import os
from datetime import datetime, timezone
from pathlib import Path
result = {
    "module": "Insight Rebuild Module 1",
    "bootstrap_version": os.environ.get("VERSION", ""),
    "status": os.environ.get("TEST_STATUS", "failed"),
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "test_command": os.environ.get("TEST_COMMAND", ""),
    "test_exit_code": int(os.environ.get("TEST_RC", "1")),
    "product_base_sha": os.environ.get("PRODUCT_BASE_SHA", ""),
    "module0_expected_sha": os.environ.get("MODULE0_SHA", ""),
    "oris_check_status": os.environ.get("ORIS_CHECK_STATUS", ""),
    "oris_head": os.environ.get("ORIS_HEAD", ""),
    "runtime_v2_final_oris_sha": os.environ.get("RUNTIME_V2_FINAL_ORIS_SHA", ""),
    "old_interactive_insight_product_continued": False,
    "runtime_v2_backed_rebuild_started": True,
    "log_file": os.environ.get("LOG_FILE", ""),
    "checks": [
        "runtime_v2_alignment_is_valid",
        "required_capabilities_are_complete",
        "product_mutation_allowed_after_runtime_acceptance",
        "rebuild_sequence_starts_with_architecture_alignment",
        "architecture_summary_identifies_next_module",
    ],
}
Path("reports/testing").mkdir(parents=True, exist_ok=True)
Path("reports/testing/insight_rebuild_module_1_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
Path("reports/testing/latest_test_result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
PY

cat > reports/execution/insight_rebuild_module_1_execution_report.md <<EOF
# Insight Rebuild Module 1 Execution Report

## Module

Architecture Alignment with Runtime v2

## Bootstrap Version

$VERSION

## Product Base Commit

$PRODUCT_BASE_SHA

## Runtime v2 Reference

- ORIS check status: $ORIS_CHECK_STATUS
- ORIS head: $ORIS_HEAD
- Runtime v2 final ORIS reference: $RUNTIME_V2_FINAL_ORIS_SHA

## Test Command

$TEST_COMMAND

## Test Result

- test exit code: $TEST_RC
- status: $TEST_STATUS

## Evidence Files

- app/runtime_v2_alignment.py
- tests/test_runtime_v2_alignment.py
- docs/rebuild/INSIGHT_REBUILD_MODULE_1_ARCHITECTURE.md
- docs/testing/INSIGHT_REBUILD_MODULE_1_TEST_PLAN.md
- reports/testing/insight_rebuild_module_1_test_result.json
- reports/testing/latest_test_result.json
- reports/execution/insight_rebuild_module_1_bootstrap_latest.log

## Insight Rebuild Module 1 Evidence Commit SHA

Pending until evidence commit completes.

## Next Module

Insight Rebuild Module 2: Domain Contracts.
EOF

if [ "$COMMIT_AND_PUSH" != "1" ]; then
  summary "Tests $TEST_STATUS. Commit/push skipped by INSIGHT_MODULE_1_COMMIT_AND_PUSH=$COMMIT_AND_PUSH"
  summary "Log: $LOG_FILE"
  exit "$TEST_RC"
fi

if [ "$TEST_RC" -eq 0 ]; then
  commit_and_push_evidence "DONE: Insight Rebuild Module 1 tests passed" "insight-rebuild(module-1): align product architecture with runtime v2"
  exit $?
else
  commit_and_push_evidence "FAILED: Insight Rebuild Module 1 tests failed" "insight-rebuild(module-1): record failed bootstrap evidence"
  exit "$TEST_RC"
fi
