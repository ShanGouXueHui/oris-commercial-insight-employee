from __future__ import annotations

import os
from typing import Iterable, Mapping

MODULE_35_LOCAL_RECEIPT_BUNDLE_VERSION = "2026-06-26-module-35"
MAX_RECEIPT_BUNDLE_SIZE = 100


def _env_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def local_receipt_bundle_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_LOCAL_RECEIPT_BUNDLE_ENABLED", False)


def _bounded_receipts(receipts: Iterable[Mapping[str, object]]) -> list[Mapping[str, object]]:
    items = list(receipts)
    if len(items) > MAX_RECEIPT_BUNDLE_SIZE:
        return items[:MAX_RECEIPT_BUNDLE_SIZE]
    return items


def build_local_receipt_bundle_summary(
    receipts: Iterable[Mapping[str, object]],
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    if not local_receipt_bundle_enabled(values):
        return {
            "allowed": False,
            "reason": "local_receipt_bundle_disabled",
            "local_receipt_bundle_version": MODULE_35_LOCAL_RECEIPT_BUNDLE_VERSION,
            "bundle_visible": False,
            "file_written": False,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
        }
    bounded = _bounded_receipts(receipts)
    verified_true = sum(1 for receipt in bounded if receipt.get("verified") is True)
    verified_false = sum(1 for receipt in bounded if receipt.get("verified") is False)
    checksum_count = sum(1 for receipt in bounded if receipt.get("checksum"))
    return {
        "allowed": True,
        "reason": "local_receipt_bundle_visible",
        "receipt_count": len(bounded),
        "verified_true_count": verified_true,
        "verified_false_count": verified_false,
        "checksum_count": checksum_count,
        "max_receipt_bundle_size": MAX_RECEIPT_BUNDLE_SIZE,
        "local_receipt_bundle_version": MODULE_35_LOCAL_RECEIPT_BUNDLE_VERSION,
        "bundle_visible": True,
        "file_written": False,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def summarize_local_receipt_bundle(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = local_receipt_bundle_enabled(values)
    return {
        "local_receipt_bundle_version": MODULE_35_LOCAL_RECEIPT_BUNDLE_VERSION,
        "enabled": enabled,
        "enabled_by_default": False,
        "bundle_visible": enabled,
        "file_written": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }
