from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

MODULE_30_TENANT_OPERATIONAL_AUDIT_RETENTION_VERSION = "2026-06-25-module-30"
DEFAULT_RETENTION_DAYS = 90
MIN_RETENTION_DAYS = 1
MAX_RETENTION_DAYS = 3650


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
