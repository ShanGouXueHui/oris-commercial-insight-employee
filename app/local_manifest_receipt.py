from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Mapping

from app.tenant_operational_audit_retention import build_local_manifest_checksum, verify_local_manifest_checksum

MODULE_34_LOCAL_MANIFEST_RECEIPT_VERSION = "2026-06-26-module-34"


def _env_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def local_manifest_receipt_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_LOCAL_MANIFEST_RECEIPT_ENABLED", False)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_local_manifest_receipt(
    manifest: Mapping[str, object],
    expected_checksum: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    if not local_manifest_receipt_enabled(values):
        return {
            "allowed": False,
            "reason": "local_manifest_receipt_disabled",
            "local_manifest_receipt_version": MODULE_34_LOCAL_MANIFEST_RECEIPT_VERSION,
            "receipt_visible": False,
            "file_written": False,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
        }
    checksum = build_local_manifest_checksum(
        manifest,
        env={"ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED": "true"},
    )["checksum"]
    verified = None
    if expected_checksum is not None:
        verification = verify_local_manifest_checksum(
            manifest,
            expected_checksum,
            env={"ORIS_INSIGHT_LOCAL_MANIFEST_VERIFICATION_ENABLED": "true"},
        )
        verified = verification["verified"]
    return {
        "allowed": True,
        "reason": "local_manifest_receipt_visible",
        "receipt_id": str(uuid.uuid4()),
        "receipt_generated_at": _now(),
        "checksum_algorithm": "sha256",
        "checksum": checksum,
        "verified": verified,
        "local_manifest_receipt_version": MODULE_34_LOCAL_MANIFEST_RECEIPT_VERSION,
        "receipt_visible": True,
        "file_written": False,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def summarize_local_manifest_receipt(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = local_manifest_receipt_enabled(values)
    return {
        "local_manifest_receipt_version": MODULE_34_LOCAL_MANIFEST_RECEIPT_VERSION,
        "enabled": enabled,
        "enabled_by_default": False,
        "receipt_visible": enabled,
        "file_written": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }
