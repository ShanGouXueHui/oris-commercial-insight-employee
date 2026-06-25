from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Mapping

from app.commercial_guardrails import GuardrailDecision, GuardrailLedger, evaluate_guardrails
from app.config import CommercialGuardrailsSettings, TenantGuardrailsSettings
from app.tenant_entitlements import (
    DEFAULT_PLANS,
    EntitlementDecision,
    TenantEntitlementRecord,
    TenantRecord,
    UsageRecord,
    build_default_entitlement,
    evaluate_entitlement,
)
from app.tenant_usage_ledger import (
    DEFAULT_TENANT_USAGE_LEDGER,
    MODULE_24_TENANT_USAGE_LEDGER_VERSION,
    TenantUsageLedger,
)

MODULE_22_TENANT_GUARDRAIL_VERSION = "2026-06-25-module-22"
MODULE_23_TENANT_MIDDLEWARE_VERSION = "2026-06-25-module-23"
MODULE_25_TENANT_MIDDLEWARE_USAGE_LEDGER_VERSION = "2026-06-25-module-25"
TENANT_GUARDRAIL_BLOCKING_MODES = {"blocking", "enforce", "enforced"}
TENANT_GUARDRAIL_OBSERVE_MODES = {"observe", "monitor", "disabled", "off"}


@dataclass(frozen=True)
class TenantGuardrailPolicy:
    entitlement_enforcement_mode: str = "observe"
    require_tenant_entitlement: bool = False
    tenant_header: str = "x-tenant-id"
    default_tenant_id: str = "anonymous"
    billing_provider_integrated: bool = False
    payment_processing_enabled: bool = False
    tenant_usage_ledger_enabled: bool = False
    tenant_usage_consume_on_allowed_request: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TenantGuardrailDecision:
    allowed: bool
    status_code: int
    tenant_id: str
    client_id: str
    reason: str
    tenant_guardrail_version: str
    commercial_guardrail: dict[str, object]
    entitlement: dict[str, object] | None
    entitlement_enforcement_mode: str
    billing_provider_integrated: bool = False
    payment_processing_enabled: bool = False
    tenant_middleware_usage_ledger_version: str = MODULE_25_TENANT_MIDDLEWARE_USAGE_LEDGER_VERSION
    tenant_usage_ledger_enabled: bool = False
    tenant_usage_ledger_version: str | None = None
    tenant_usage_request_count: int | None = None
    tenant_usage_consumed: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _header_get(headers: Mapping[str, str], name: str) -> str | None:
    lower_name = name.lower()
    for key, value in headers.items():
        if key.lower() == lower_name:
            return value
    return None


def _tenant_id_from_headers(headers: Mapping[str, str], policy: TenantGuardrailPolicy) -> str:
    tenant_id = _header_get(headers, policy.tenant_header)
    if tenant_id:
        return tenant_id[:80]
    return policy.default_tenant_id


def tenant_guardrail_policy_from_settings(settings: TenantGuardrailsSettings) -> TenantGuardrailPolicy:
    return TenantGuardrailPolicy(
        entitlement_enforcement_mode=settings.entitlement_enforcement_mode,
        require_tenant_entitlement=settings.require_tenant_entitlement,
        tenant_header=settings.tenant_header,
        default_tenant_id=settings.default_tenant_id,
        billing_provider_integrated=settings.billing_provider_integrated,
        payment_processing_enabled=settings.payment_processing_enabled,
        tenant_usage_ledger_enabled=settings.tenant_usage_ledger_enabled,
        tenant_usage_consume_on_allowed_request=settings.tenant_usage_consume_on_allowed_request,
    )


def build_local_tenant_entitlements(settings: TenantGuardrailsSettings) -> tuple[TenantEntitlementRecord, ...]:
    if not settings.local_entitlements_enabled:
        return ()
    plan = next((item for item in DEFAULT_PLANS if item.plan_id == settings.local_plan_id), DEFAULT_PLANS[0])
    tenant = TenantRecord(tenant_id=settings.local_tenant_id, display_name=settings.local_tenant_id)
    return (build_default_entitlement(tenant, plan, effective_from="2026-06-25T00:00:00+00:00"),)


def _base_decision(
    allowed: bool,
    status_code: int,
    tenant_id: str,
    commercial_decision: GuardrailDecision,
    entitlement_decision: EntitlementDecision | None,
    policy: TenantGuardrailPolicy,
    reason: str,
    usage: UsageRecord | None = None,
    usage_consumed: bool = False,
) -> TenantGuardrailDecision:
    return TenantGuardrailDecision(
        allowed=allowed,
        status_code=status_code,
        tenant_id=tenant_id,
        client_id=commercial_decision.client_id,
        reason=reason,
        tenant_guardrail_version=MODULE_22_TENANT_GUARDRAIL_VERSION,
        commercial_guardrail=commercial_decision.to_dict(),
        entitlement=entitlement_decision.to_dict() if entitlement_decision else None,
        entitlement_enforcement_mode=policy.entitlement_enforcement_mode,
        billing_provider_integrated=policy.billing_provider_integrated,
        payment_processing_enabled=policy.payment_processing_enabled,
        tenant_usage_ledger_enabled=policy.tenant_usage_ledger_enabled,
        tenant_usage_ledger_version=MODULE_24_TENANT_USAGE_LEDGER_VERSION if policy.tenant_usage_ledger_enabled else None,
        tenant_usage_request_count=usage.request_count if usage else None,
        tenant_usage_consumed=usage_consumed,
    )


def _usage_from_ledger(
    tenant_id: str,
    usage: UsageRecord | None,
    policy: TenantGuardrailPolicy,
    tenant_usage_ledger: TenantUsageLedger | None,
    now: datetime | None,
) -> UsageRecord | None:
    if usage is not None or not policy.tenant_usage_ledger_enabled:
        return usage
    active_ledger = tenant_usage_ledger or DEFAULT_TENANT_USAGE_LEDGER
    return active_ledger.get_usage(tenant_id, now=now)


def _consume_usage_if_configured(
    tenant_id: str,
    usage: UsageRecord | None,
    policy: TenantGuardrailPolicy,
    tenant_usage_ledger: TenantUsageLedger | None,
    now: datetime | None,
) -> tuple[UsageRecord | None, bool]:
    if not (policy.tenant_usage_ledger_enabled and policy.tenant_usage_consume_on_allowed_request):
        return usage, False
    active_ledger = tenant_usage_ledger or DEFAULT_TENANT_USAGE_LEDGER
    return active_ledger.consume(tenant_id, now=now), True


def _allowed_decision(
    tenant_id: str,
    commercial_decision: GuardrailDecision,
    entitlement_decision: EntitlementDecision | None,
    policy: TenantGuardrailPolicy,
    reason: str,
    usage: UsageRecord | None,
    tenant_usage_ledger: TenantUsageLedger | None,
    now: datetime | None,
) -> TenantGuardrailDecision:
    final_usage, usage_consumed = _consume_usage_if_configured(
        tenant_id,
        usage,
        policy,
        tenant_usage_ledger,
        now,
    )
    return _base_decision(
        allowed=True,
        status_code=200,
        tenant_id=tenant_id,
        commercial_decision=commercial_decision,
        entitlement_decision=entitlement_decision,
        policy=policy,
        reason=reason,
        usage=final_usage,
        usage_consumed=usage_consumed,
    )


def evaluate_tenant_entitlement_guardrails(
    path: str,
    method: str,
    headers: Mapping[str, str],
    settings: CommercialGuardrailsSettings,
    entitlements: tuple[TenantEntitlementRecord, ...],
    usage: UsageRecord | None = None,
    policy: TenantGuardrailPolicy | None = None,
    ledger: GuardrailLedger | None = None,
    now: datetime | None = None,
    tenant_usage_ledger: TenantUsageLedger | None = None,
) -> TenantGuardrailDecision:
    active_policy = policy or TenantGuardrailPolicy()
    tenant_id = _tenant_id_from_headers(headers, active_policy)
    commercial_decision = evaluate_guardrails(path, method, headers, settings, ledger=ledger, now=now)
    if not commercial_decision.allowed:
        return _base_decision(
            allowed=False,
            status_code=commercial_decision.status_code,
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=None,
            policy=active_policy,
            reason=f"commercial_guardrail_{commercial_decision.reason}",
        )
    if commercial_decision.reason == "exempt_path":
        return _base_decision(
            allowed=True,
            status_code=200,
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=None,
            policy=active_policy,
            reason="exempt_path_entitlement_skipped",
        )
    active_usage = _usage_from_ledger(tenant_id, usage, active_policy, tenant_usage_ledger, now)
    entitlement_decision = evaluate_entitlement(tenant_id, entitlements, active_usage)
    entitlement_mode = active_policy.entitlement_enforcement_mode.strip().lower()
    if entitlement_mode in TENANT_GUARDRAIL_OBSERVE_MODES:
        return _allowed_decision(
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=entitlement_decision,
            policy=active_policy,
            reason="tenant_entitlement_observe_mode",
            usage=active_usage,
            tenant_usage_ledger=tenant_usage_ledger,
            now=now,
        )
    if entitlement_mode not in TENANT_GUARDRAIL_BLOCKING_MODES:
        return _allowed_decision(
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=entitlement_decision,
            policy=active_policy,
            reason="tenant_entitlement_unknown_mode_fails_open",
            usage=active_usage,
            tenant_usage_ledger=tenant_usage_ledger,
            now=now,
        )
    if active_policy.require_tenant_entitlement and not entitlement_decision.allowed:
        return _base_decision(
            allowed=False,
            status_code=429 if entitlement_decision.reason == "monthly_quota_exceeded" else 403,
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=entitlement_decision,
            policy=active_policy,
            reason=f"tenant_entitlement_{entitlement_decision.reason}",
            usage=active_usage,
        )
    return _allowed_decision(
        tenant_id=tenant_id,
        commercial_decision=commercial_decision,
        entitlement_decision=entitlement_decision,
        policy=active_policy,
        reason="tenant_entitlement_allowed",
        usage=active_usage,
        tenant_usage_ledger=tenant_usage_ledger,
        now=now,
    )


def summarize_tenant_guardrail_bridge(policy: TenantGuardrailPolicy | None = None) -> dict[str, object]:
    active_policy = policy or TenantGuardrailPolicy()
    return {
        "tenant_guardrail_version": MODULE_22_TENANT_GUARDRAIL_VERSION,
        "commercial_guardrail_bridge": True,
        "tenant_entitlement_bridge": True,
        "entitlement_enforcement_mode": active_policy.entitlement_enforcement_mode,
        "require_tenant_entitlement": active_policy.require_tenant_entitlement,
        "billing_provider_integrated": active_policy.billing_provider_integrated,
        "payment_processing_enabled": active_policy.payment_processing_enabled,
        "tenant_usage_ledger_enabled": active_policy.tenant_usage_ledger_enabled,
        "tenant_usage_consume_on_allowed_request": active_policy.tenant_usage_consume_on_allowed_request,
        "local_deterministic_only": True,
    }


def summarize_tenant_middleware_activation(settings: TenantGuardrailsSettings) -> dict[str, object]:
    return {
        "tenant_middleware_version": MODULE_23_TENANT_MIDDLEWARE_VERSION,
        "tenant_guardrails_enabled": settings.enabled,
        "local_entitlements_enabled": settings.local_entitlements_enabled,
        "entitlement_enforcement_mode": settings.entitlement_enforcement_mode,
        "require_tenant_entitlement": settings.require_tenant_entitlement,
        "tenant_usage_ledger_enabled": settings.tenant_usage_ledger_enabled,
        "tenant_usage_consume_on_allowed_request": settings.tenant_usage_consume_on_allowed_request,
        "billing_provider_integrated": settings.billing_provider_integrated,
        "payment_processing_enabled": settings.payment_processing_enabled,
        "default_behavior_changed": settings.enabled,
    }


def summarize_tenant_middleware_usage_ledger_bridge(settings: TenantGuardrailsSettings) -> dict[str, object]:
    request_path_changed = settings.enabled and (
        settings.tenant_usage_ledger_enabled or settings.tenant_usage_consume_on_allowed_request
    )
    return {
        "tenant_middleware_usage_ledger_version": MODULE_25_TENANT_MIDDLEWARE_USAGE_LEDGER_VERSION,
        "tenant_middleware_version": MODULE_23_TENANT_MIDDLEWARE_VERSION,
        "tenant_usage_ledger_version": MODULE_24_TENANT_USAGE_LEDGER_VERSION,
        "tenant_guardrails_enabled": settings.enabled,
        "tenant_usage_ledger_enabled": settings.tenant_usage_ledger_enabled,
        "tenant_usage_consume_on_allowed_request": settings.tenant_usage_consume_on_allowed_request,
        "request_path_unchanged_by_default": not request_path_changed,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
        "billing_provider_integrated": settings.billing_provider_integrated,
        "payment_processing_enabled": settings.payment_processing_enabled,
    }
