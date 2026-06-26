from __future__ import annotations

import hashlib
import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

MODULE_30_TENANT_OPERATIONAL_AUDIT_RETENTION_VERSION = "2026-06-25-module-30"
MODULE_31_LOCAL_AUDIT_MANIFEST_VERSION = "2026-06-25-module-31"
MODULE_32_LOCAL_MANIFEST_CHECKSUM_VERSION = "2026-06-26-module-32"
DEFAULT_RETENTION_DAYS = 90
MIN_RETENTION_DAYS = 1
MAX_RETENTION_DAYS = 3650
MAX_MANIFEST_EVENT_COUNT = 1000


def _env_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(values: Mapping[str, str], name: str, default: int) -> int:
    raw = values.get(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _bounded_days(days: int) -> int:
    if days < MIN_RETENTION_DAYS:
        return MIN_RETENTION_DAYS
    if days > MAX_RETENTION_DAYS:
        return MAX_RETENTION_DAYS
    return days


def _bounded_count(value: int) -> int:
    if value < 0:
        return 0
    if value > MAX_MANIFEST_EVENT_COUNT:
        return MAX_MANIFEST_EVENT_COUNT
    return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TenantOperationalAuditRetentionPolicy:
    enabled: bool = False
    retention_days: int = DEFAULT_RETENTION_DAYS
    visibility_only: bool = True
    version: str = MODULE_30_TENANT_OPERATIONAL_AUDIT_RETENTION_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_operational_audit_retention_version": self.version,
            "enabled": self.enabled,
            "retention_days": _bounded_days(self.retention_days),
            "visibility_only": self.visibility_only,
            "explicit_configuration_required": True,
            "request_path_unchanged_by_default": not self.enabled,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
            "billing_provider_integrated": False,
            "payment_processing_enabled": False,
        }


def build_tenant_operational_audit_retention_policy(
    env: Mapping[str, str] | None = None,
) -> TenantOperationalAuditRetentionPolicy:
    values = os.environ if env is None else env
    return TenantOperationalAuditRetentionPolicy(
        enabled=_env_bool(values, "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_RETENTION_ENABLED", False),
        retention_days=_bounded_days(
            _env_int(values, "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)
        ),
    )


def summarize_tenant_operational_audit_retention_policy(
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    return build_tenant_operational_audit_retention_policy(env=env).to_dict()


def local_audit_manifest_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_LOCAL_AUDIT_MANIFEST_ENABLED", False)


def build_local_audit_manifest(
    event_count: int = 0,
    tenant_id: str | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    if not local_audit_manifest_enabled(values):
        return {
            "allowed": False,
            "reason": "local_audit_manifest_disabled",
            "local_audit_manifest_version": MODULE_31_LOCAL_AUDIT_MANIFEST_VERSION,
            "manifest_only": True,
            "file_written": False,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
        }
    return {
        "allowed": True,
        "reason": "local_audit_manifest_generated",
        "manifest_id": str(uuid.uuid4()),
        "tenant_id": tenant_id,
        "event_count": _bounded_count(int(event_count)),
        "generated_at": _utc_now(),
        "local_audit_manifest_version": MODULE_31_LOCAL_AUDIT_MANIFEST_VERSION,
        "manifest_only": True,
        "file_written": False,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def summarize_local_audit_manifest(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = local_audit_manifest_enabled(values)
    return {
        "local_audit_manifest_version": MODULE_31_LOCAL_AUDIT_MANIFEST_VERSION,
        "enabled": enabled,
        "enabled_by_default": False,
        "manifest_only": True,
        "file_written": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def local_manifest_checksum_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_LOCAL_MANIFEST_CHECKSUM_ENABLED", False)


def build_local_manifest_checksum(
    manifest: Mapping[str, object],
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    if not local_manifest_checksum_enabled(values):
        return {
            "allowed": False,
            "reason": "local_manifest_checksum_disabled",
            "local_manifest_checksum_version": MODULE_32_LOCAL_MANIFEST_CHECKSUM_VERSION,
            "checksum_visible": False,
            "file_written": False,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
        }
    canonical = json.dumps(dict(manifest), sort_keys=True, separators=(",", ":"), default=str)
    checksum = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {
        "allowed": True,
        "reason": "local_manifest_checksum_visible",
        "checksum_algorithm": "sha256",
        "checksum": checksum,
        "local_manifest_checksum_version": MODULE_32_LOCAL_MANIFEST_CHECKSUM_VERSION,
        "checksum_visible": True,
        "file_written": False,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }


def summarize_local_manifest_checksum(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = local_manifest_checksum_enabled(values)
    return {
        "local_manifest_checksum_version": MODULE_32_LOCAL_MANIFEST_CHECKSUM_VERSION,
        "enabled": enabled,
        "enabled_by_default": False,
        "checksum_visible": enabled,
        "file_written": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }
