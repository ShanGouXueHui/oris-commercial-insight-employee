from __future__ import annotations

import os
from typing import Mapping

MODULE_36_LOCAL_RECEIPT_BUNDLE_HEALTH_VERSION = "2026-06-26-module-36"


def _env_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def local_receipt_bundle_health_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_HEALTH_ENABLED", False)


def build_local_receipt_bundle_health(
    bundle_summary: Mapping[str, object],
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    if not local_receipt_bundle_health_enabled(values):
        return {
            "allowed": False,
            "reason": "local_receipt_bundle_health_disabled",
            "local_receipt_bundle_health_version": MODULE_36_LOCAL_RECEIPT_BUNDLE_HEALTH_VERSION,
            "health_visible": False,
            "file_written": False,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
        }
    receipt_count = int(bundle_summary.get("receipt_count", 0) or 0)
    verified_true = int(bundle_summary.get("verified_true_count", 0) or 0)
    verified_false = int(bundle_summary.get("verified_false_count", 0) or 0)
    checksum_count = int(bundle_summary.get("checksum_count", 0) or 0)
    missing_checksum = max(receipt_count - checksum_count, 0)
    if receipt_count == 0:
        health_status = "empty"
    elif verified_false > 0 or missing_checksum > 0:
        health_status = "attention_required"
    elif verified_true == receipt_count:
        health_status = "healthy"
    else:
        health_status = "partial"
    return {
        "allowed": True,
        "reason": "local_receipt_bundle_health_visible",
        "health_status": health_status,
        "receipt_count": receipt_count,
        "verified_true_count": verified_true,
        "verified_false_count": verified_false,
        "missing_checksum_count": missing_checksum,
        "local_receipt_bundle_health_version": MODULE_36_LOCAL_RECEIPT_BUNDLE_HEALTH_VERSION,
        "health_visible": True,
        "file_written": False,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def summarize_local_receipt_bundle_health(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = local_receipt_bundle_health_enabled(values)
    return {
        "local_receipt_bundle_health_version": MODULE_36_LOCAL_RECEIPT_BUNDLE_HEALTH_VERSION,
        "enabled": enabled,
        "enabled_by_default": False,
        "health_visible": enabled,
        "file_written": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }
