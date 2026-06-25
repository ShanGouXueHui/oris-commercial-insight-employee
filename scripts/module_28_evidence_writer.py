from __future__ import annotations

import json
import os
from pathlib import Path

VERSION = os.environ.get("VERSION", "2026-06-25-insight-rebuild-module-28-official")
TEST_RC = int(os.environ.get("TEST_RC", "1"))
STATUS = "passed" if TEST_RC == 0 else "failed"
TEST_COMMAND = os.environ.get("TEST_COMMAND", "")
PRODUCT_BASE_SHA = os.environ.get("PRODUCT_BASE_SHA", "")
LOG_FILE = os.environ.get("LOG_FILE", "")

payload = {
    "module": "Insight Rebuild Module 28",
    "bootstrap_version": VERSION,
    "status": STATUS,
    "test_command": TEST_COMMAND,
    "test_exit_code": TEST_RC,
    "product_base_sha": PRODUCT_BASE_SHA,
    "expected_unit_test_count": 168,
    "log_file": LOG_FILE,
    "checks": [
        "prior_module_test_compatibility",
        "default_operational_audit_disabled",
        "in_memory_audit_records_and_lists_events",
        "sqlite_audit_persists_across_instances",
        "builder_uses_sqlite_only_when_configured",
        "health_details_reports_module_28_audit_summary",
    ],
    "tenant_operational_audit_trail": True,
    "tenant_operational_audit_default_enabled": False,
    "in_memory_audit_supported": True,
    "sqlite_audit_supported": True,
    "explicit_configuration_required": True,
    "request_path_unchanged_by_default": True,
    "tenant_operational_audit_version": "2026-06-25-module-28",
    "external_storage_enabled": False,
    "live_external_action_enabled": False,
    "billing_provider_integrated": False,
    "payment_processing_enabled": False,
}

Path("reports/testing").mkdir(parents=True, exist_ok=True)
Path("reports/execution").mkdir(parents=True, exist_ok=True)
Path("reports/testing/insight_rebuild_module_28_test_result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
Path("reports/testing/latest_test_result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
Path("reports/execution/insight_rebuild_module_28_execution_report.md").write_text(
    "# Insight Rebuild Module 28 Execution Report\n\n"
    "## Module\n\nInsight Rebuild Module 28\n\n"
    f"## Bootstrap Version\n\n{VERSION}\n\n"
    f"## Product Base Commit\n\n{PRODUCT_BASE_SHA}\n\n"
    f"## Test Command\n\n{TEST_COMMAND}\n\n"
    f"## Test Result\n\n- test exit code: {TEST_RC}\n- status: {STATUS}\n- expected unit test count: 168\n\n"
    "## Evidence Commit SHA\n\nPending until evidence commit completes.\n\n"
    "## Next Module\n\nModule 29 should proceed only after Module 28 user-controlled evidence is pushed and verified.\n",
    encoding="utf-8",
)
