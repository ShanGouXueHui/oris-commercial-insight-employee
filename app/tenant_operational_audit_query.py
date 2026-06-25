from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from app.tenant_operational_audit import TenantOperationalAuditTrail, build_tenant_operational_audit_trail

MODULE_29_TENANT_OPERATIONAL_AUDIT_QUERY_VERSION = "2026-06-25-module-29"
MAX_AUDIT_QUERY_LIMIT = 100


def _env_bool(values: Mapping[str, str], name: str, default: bool) -> bool:
    raw = values.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class TenantOperationalAuditQueryRequest:
    tenant_id: str | None = None
    limit: int = 50

    def bounded_limit(self) -> int:
        if self.limit < 1:
            return 1
        if self.limit > MAX_AUDIT_QUERY_LIMIT:
            return MAX_AUDIT_QUERY_LIMIT
        return self.limit

    def clean_tenant_id(self) -> str | None:
        if self.tenant_id is None:
            return None
        value = self.tenant_id.strip()[:80]
        return value or None


@dataclass(frozen=True)
class TenantOperationalAuditQueryResult:
    allowed: bool
    reason: str
    tenant_id: str | None
    limit: int
    events: list[dict[str, object]]
    query_version: str = MODULE_29_TENANT_OPERATIONAL_AUDIT_QUERY_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "tenant_id": self.tenant_id,
            "limit": self.limit,
            "events": self.events,
            "event_count": len(self.events),
            "query_version": self.query_version,
            "read_only": True,
            "external_storage_enabled": False,
            "live_external_action_enabled": False,
            "billing_provider_integrated": False,
            "payment_processing_enabled": False,
        }


def tenant_operational_audit_query_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    return _env_bool(values, "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_QUERY_ENABLED", False)


def query_tenant_operational_audit(
    request: TenantOperationalAuditQueryRequest,
    trail: TenantOperationalAuditTrail | None = None,
    env: Mapping[str, str] | None = None,
) -> TenantOperationalAuditQueryResult:
    values = os.environ if env is None else env
    if not tenant_operational_audit_query_enabled(values):
        return TenantOperationalAuditQueryResult(
            allowed=False,
            reason="tenant_operational_audit_query_disabled",
            tenant_id=request.clean_tenant_id(),
            limit=request.bounded_limit(),
            events=[],
        )
    active_trail = trail or build_tenant_operational_audit_trail(env=values)
    events = active_trail.list_events(tenant_id=request.clean_tenant_id(), limit=request.bounded_limit())
    return TenantOperationalAuditQueryResult(
        allowed=True,
        reason="tenant_operational_audit_query_allowed",
        tenant_id=request.clean_tenant_id(),
        limit=request.bounded_limit(),
        events=[event.to_dict() for event in events],
    )


def summarize_tenant_operational_audit_query(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    enabled = tenant_operational_audit_query_enabled(values)
    return {
        "tenant_operational_audit_query_version": MODULE_29_TENANT_OPERATIONAL_AUDIT_QUERY_VERSION,
        "enabled": enabled,
        "read_only": True,
        "enabled_by_default": False,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not enabled,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
        "billing_provider_integrated": False,
        "payment_processing_enabled": False,
    }
