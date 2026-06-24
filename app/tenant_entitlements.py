from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Iterable

MODULE_16_TENANT_ENTITLEMENT_VERSION = "2026-06-24-module-16"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TenantRecord:
    tenant_id: str
    display_name: str
    status: str = "active"
    created_at: str = ""

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["created_at"] = self.created_at or _utc_now()
        return payload


@dataclass(frozen=True)
class PlanRecord:
    plan_id: str
    display_name: str
    monthly_request_quota: int
    per_minute_request_limit: int
    seat_limit: int
    status: str = "active"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TenantEntitlementRecord:
    tenant_id: str
    plan_id: str
    monthly_request_quota: int
    per_minute_request_limit: int
    seat_limit: int
    effective_from: str
    effective_to: str | None = None
    status: str = "active"

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class UsageRecord:
    tenant_id: str
    period: str
    request_count: int
    updated_at: str = ""

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["updated_at"] = self.updated_at or _utc_now()
        return payload


@dataclass(frozen=True)
class EntitlementDecision:
    allowed: bool
    tenant_id: str
    plan_id: str | None
    reason: str
    remaining_monthly_requests: int | None
    per_minute_request_limit: int | None
    entitlement_version: str = MODULE_16_TENANT_ENTITLEMENT_VERSION

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


DEFAULT_PLANS: tuple[PlanRecord, ...] = (
    PlanRecord(plan_id="free", display_name="Free", monthly_request_quota=100, per_minute_request_limit=10, seat_limit=1),
    PlanRecord(plan_id="team", display_name="Team", monthly_request_quota=5000, per_minute_request_limit=60, seat_limit=10),
    PlanRecord(plan_id="enterprise", display_name="Enterprise", monthly_request_quota=100000, per_minute_request_limit=600, seat_limit=250),
)

TENANT_SCHEMA_TABLES = (
    "tenants",
    "plans",
    "tenant_entitlements",
    "tenant_usage",
)


def build_default_entitlement(tenant: TenantRecord, plan: PlanRecord, effective_from: str | None = None) -> TenantEntitlementRecord:
    return TenantEntitlementRecord(
        tenant_id=tenant.tenant_id,
        plan_id=plan.plan_id,
        monthly_request_quota=plan.monthly_request_quota,
        per_minute_request_limit=plan.per_minute_request_limit,
        seat_limit=plan.seat_limit,
        effective_from=effective_from or _utc_now(),
    )


def evaluate_entitlement(
    tenant_id: str,
    entitlements: Iterable[TenantEntitlementRecord],
    usage: UsageRecord | None = None,
) -> EntitlementDecision:
    active = [item for item in entitlements if item.tenant_id == tenant_id and item.status == "active"]
    if not active:
        return EntitlementDecision(
            allowed=False,
            tenant_id=tenant_id,
            plan_id=None,
            reason="tenant_entitlement_missing",
            remaining_monthly_requests=None,
            per_minute_request_limit=None,
        )
    entitlement = active[0]
    used = usage.request_count if usage and usage.tenant_id == tenant_id else 0
    remaining = max(entitlement.monthly_request_quota - used, 0)
    if used >= entitlement.monthly_request_quota:
        return EntitlementDecision(
            allowed=False,
            tenant_id=tenant_id,
            plan_id=entitlement.plan_id,
            reason="monthly_quota_exceeded",
            remaining_monthly_requests=0,
            per_minute_request_limit=entitlement.per_minute_request_limit,
        )
    return EntitlementDecision(
        allowed=True,
        tenant_id=tenant_id,
        plan_id=entitlement.plan_id,
        reason="entitlement_allowed",
        remaining_monthly_requests=remaining,
        per_minute_request_limit=entitlement.per_minute_request_limit,
    )


def render_tenant_schema_manifest() -> dict[str, object]:
    return {
        "schema_version": MODULE_16_TENANT_ENTITLEMENT_VERSION,
        "tables": list(TENANT_SCHEMA_TABLES),
        "default_plans": [plan.to_dict() for plan in DEFAULT_PLANS],
        "billing_provider_integrated": False,
        "payment_processing_enabled": False,
        "invoice_generation_enabled": False,
        "quota_enforcement_boundary": True,
        "tenant_isolation_boundary": True,
        "non_scope": ["real_payment_processing", "invoice_generation", "tax_calculation", "revenue_recognition"],
    }


def summarize_tenant_entitlement_boundary() -> dict[str, object]:
    manifest = render_tenant_schema_manifest()
    return {
        "entitlement_version": MODULE_16_TENANT_ENTITLEMENT_VERSION,
        "table_count": len(manifest["tables"]),
        "tables": manifest["tables"],
        "default_plan_ids": [plan.plan_id for plan in DEFAULT_PLANS],
        "billing_provider_integrated": False,
        "payment_processing_enabled": False,
        "invoice_generation_enabled": False,
        "tenant_isolation_boundary": True,
        "quota_enforcement_boundary": True,
    }
