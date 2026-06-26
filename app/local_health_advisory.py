from __future__ import annotations

import os
from typing import Mapping

MODULE_37_LOCAL_HEALTH_ADVISORY_VERSION = "2026-06-26-module-37"


def _env_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def local_health_advisory_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_LOCAL_HEALTH_ADVISORY_ENABLED", False)


def build_local_health_advisory(
    health_summary: Mapping[str, object],
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    if not local_health_advisory_enabled(values):
        return {
            "allowed": False,
            "reason": "local_health_advisory_disabled",
            "local_health_advisory_version": MODULE_37_LOCAL_HEALTH_ADVISORY_VERSION,
            "advisory_visible": False,
            "file_written": False,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
        }
    status = str(health_summary.get("health_status", "unknown"))
    if status == "healthy":
        severity = "info"
        advisory = "no_action_needed"
    elif status == "attention_required":
        severity = "warning"
        advisory = "review_failed_or_missing_receipts"
    elif status == "empty":
        severity = "info"
        advisory = "no_receipts_to_review"
    else:
        severity = "notice"
        advisory = "review_partial_receipt_coverage"
    return {
        "allowed": True,
        "reason": "local_health_advisory_visible",
        "health_status": status,
        "advisory_severity": severity,
        "advisory_code": advisory,
        "local_health_advisory_version": MODULE_37_LOCAL_HEALTH_ADVISORY_VERSION,
        "advisory_visible": True,
        "file_written": False,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def summarize_local_health_advisory(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = local_health_advisory_enabled(values)
    return {
        "local_health_advisory_version": MODULE_37_LOCAL_HEALTH_ADVISORY_VERSION,
        "enabled": enabled,
        "enabled_by_default": False,
        "advisory_visible": enabled,
        "file_written": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }
