from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Mapping

from app.commercial_guardrails import GuardrailDecision, GuardrailLedger, evaluate_guardrails
from app.config import CommercialGuardrailsSettings
from app.tenant_entitlements import EntitlementDecision, TenantEntitlementRecord, UsageRecord, evaluate_entitlement

MODULE_22_TENANT_GUARDRAIL_VERSION = "2026-06-25-module-22"
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


def _base_decision(
    allowed: bool,
    status_code: int,
    tenant_id: str,
    commercial_decision: GuardrailDecision,
    entitlement_decision: EntitlementDecision | None,
    policy: TenantGuardrailPolicy,
    reason: str,
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
    entitlement_decision = evaluate_entitlement(tenant_id, entitlements, usage)
    entitlement_mode = active_policy.entitlement_enforcement_mode.strip().lower()
    if entitlement_mode in TENANT_GUARDRAIL_OBSERVE_MODES:
        return _base_decision(
            allowed=True,
            status_code=200,
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=entitlement_decision,
            policy=active_policy,
            reason="tenant_entitlement_observe_mode",
        )
    if entitlement_mode not in TENANT_GUARDRAIL_BLOCKING_MODES:
        return _base_decision(
            allowed=True,
            status_code=200,
            tenant_id=tenant_id,
            commercial_decision=commercial_decision,
            entitlement_decision=entitlement_decision,
            policy=active_policy,
            reason="tenant_entitlement_unknown_mode_fails_open",
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
        )
    return _base_decision(
        allowed=True,
        status_code=200,
        tenant_id=tenant_id,
        commercial_decision=commercial_decision,
        entitlement_decision=entitlement_decision,
        policy=active_policy,
        reason="tenant_entitlement_allowed",
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
        "local_deterministic_only": True,
    }
