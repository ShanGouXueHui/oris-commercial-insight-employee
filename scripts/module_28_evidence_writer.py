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
if "module-30" in VERSION:
    MODULE_NUMBER = "30"
elif "module-29" in VERSION:
    MODULE_NUMBER = "29"
else:
    MODULE_NUMBER = "28"
EXPECTED_COUNT = {"28": 168, "29": 174, "30": 179}[MODULE_NUMBER]
MODULE_NAME = f"Insight Rebuild Module {MODULE_NUMBER}"
RESULT_FILE = f"reports/testing/insight_rebuild_module_{MODULE_NUMBER}_test_result.json"
REPORT_FILE = f"reports/execution/insight_rebuild_module_{MODULE_NUMBER}_execution_report.md"

if MODULE_NUMBER == "30":
    checks = [
        "prior_module_test_compatibility",
        "retention_policy_disabled_by_default",
        "retention_policy_can_be_enabled_explicitly",
        "retention_days_are_bounded",
        "retention_summary_is_visibility_only",
        "invalid_retention_days_falls_back_to_default",
    ]
    flags = {
        "tenant_operational_audit_retention": True,
        "tenant_operational_audit_retention_default_enabled": False,
        "visibility_only": True,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": True,
        "tenant_operational_audit_retention_version": "2026-06-25-module-30",
    }
    next_module = "Module 31 should proceed only after Module 30 evidence is verified."
elif MODULE_NUMBER == "29":
    checks = [
        "prior_module_test_compatibility",
        "query_disabled_by_default",
        "enabled_query_returns_matching_tenant_events",
        "enabled_query_supports_all_tenants",
        "query_limit_is_bounded",
        "query_reads_sqlite_trail",
        "summary_reports_safe_defaults",
        "health_details_reports_module_29_query_summary",
    ]
    flags = {
        "tenant_operational_audit_query": True,
        "tenant_operational_audit_query_default_enabled": False,
        "read_only_query": True,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": True,
        "tenant_operational_audit_query_version": "2026-06-25-module-29",
    }
    next_module = "Module 30 should proceed only after Module 29 evidence is verified."
else:
    checks = [
        "prior_module_test_compatibility",
        "default_operational_audit_disabled",
        "in_memory_audit_records_and_lists_events",
        "sqlite_audit_persists_across_instances",
        "builder_uses_sqlite_only_when_configured",
        "health_details_reports_module_28_audit_summary",
    ]
    flags = {
        "tenant_operational_audit_trail": True,
        "tenant_operational_audit_default_enabled": False,
        "in_memory_audit_supported": True,
        "sqlite_audit_supported": True,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": True,
        "tenant_operational_audit_version": "2026-06-25-module-28",
    }
    next_module = "Module 29 should proceed only after Module 28 evidence is verified."

payload = {
    "module": MODULE_NAME,
    "bootstrap_version": VERSION,
    "status": STATUS,
    "test_command": TEST_COMMAND,
    "test_exit_code": TEST_RC,
    "product_base_sha": PRODUCT_BASE_SHA,
    "expected_unit_test_count": EXPECTED_COUNT,
    "log_file": LOG_FILE,
    "checks": checks,
    **flags,
    "external_storage_enabled": False,
    "live_external_action_enabled": False,
    "billing_provider_integrated": False,
    "payment_processing_enabled": False,
}

Path("reports/testing").mkdir(parents=True, exist_ok=True)
Path("reports/execution").mkdir(parents=True, exist_ok=True)
Path(RESULT_FILE).write_text(json.dumps(payload, indent=2), encoding="utf-8")
Path("reports/testing/latest_test_result.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
Path(REPORT_FILE).write_text(
    f"# {MODULE_NAME} Execution Report\n\n"
    f"## Module\n\n{MODULE_NAME}\n\n"
    f"## Bootstrap Version\n\n{VERSION}\n\n"
    f"## Product Base Commit\n\n{PRODUCT_BASE_SHA}\n\n"
    f"## Test Command\n\n{TEST_COMMAND}\n\n"
    f"## Test Result\n\n- test exit code: {TEST_RC}\n- status: {STATUS}\n- expected unit test count: {EXPECTED_COUNT}\n\n"
    "## Evidence Commit SHA\n\nPending until evidence commit completes.\n\n"
    f"## Next Module\n\n{next_module}\n",
    encoding="utf-8",
)
