from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from fastapi import APIRouter, Header, HTTPException, Query, Request

from app.config import TenantGuardrailsSettings, load_product_settings
from app.tenant_usage_ledger import (
    MODULE_24_TENANT_USAGE_LEDGER_VERSION,
    MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION,
    build_tenant_usage_ledger,
    summarize_tenant_usage_ledger,
)

MODULE_27_TENANT_USAGE_ADMIN_API_VERSION = "2026-06-25-module-27"
MAX_TENANT_ID_LENGTH = 80
MAX_PERIOD_LENGTH = 16

router = APIRouter(prefix="/insights/admin")


@dataclass(frozen=True)
class TenantUsageAdminPolicy:
    enabled: bool = False
    admin_header: str = "x-oris-admin-key"
    accepted_admin_keys: tuple[str, ...] = ()
    read_only: bool = True
    tenant_usage_admin_api_version: str = MODULE_27_TENANT_USAGE_ADMIN_API_VERSION
    external_storage_enabled: bool = False
    live_external_action_enabled: bool = False
    billing_provider_integrated: bool = False
    payment_processing_enabled: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["accepted_admin_keys"] = ["configured"] if self.accepted_admin_keys else []
        return payload


def tenant_usage_admin_policy_from_settings(settings: TenantGuardrailsSettings) -> TenantUsageAdminPolicy:
    return TenantUsageAdminPolicy(
        enabled=settings.tenant_usage_admin_api_enabled,
        admin_header=settings.tenant_usage_admin_header,
        accepted_admin_keys=settings.tenant_usage_admin_keys,
        billing_provider_integrated=settings.billing_provider_integrated,
        payment_processing_enabled=settings.payment_processing_enabled,
    )


def _header_get(headers: Mapping[str, str], name: str) -> str | None:
    lower_name = name.lower()
    for key, value in headers.items():
        if key.lower() == lower_name:
            return value
    return None


def _sanitize_tenant_id(tenant_id: str) -> str:
    return tenant_id.strip()[:MAX_TENANT_ID_LENGTH]


def _sanitize_period(period: str | None) -> str | None:
    if period is None:
        return None
    cleaned = period.strip()[:MAX_PERIOD_LENGTH]
    return cleaned or None


def evaluate_tenant_usage_admin_access(
    headers: Mapping[str, str],
    policy: TenantUsageAdminPolicy,
) -> dict[str, object]:
    if not policy.enabled:
        return {
            "allowed": False,
            "status_code": 404,
            "reason": "tenant_usage_admin_api_disabled",
            "policy": policy.to_dict(),
        }
    if not policy.accepted_admin_keys:
        return {
            "allowed": False,
            "status_code": 403,
            "reason": "tenant_usage_admin_key_not_configured",
            "policy": policy.to_dict(),
        }
    supplied_key = _header_get(headers, policy.admin_header)
    if supplied_key not in policy.accepted_admin_keys:
        return {
            "allowed": False,
            "status_code": 403,
            "reason": "tenant_usage_admin_key_invalid",
            "policy": policy.to_dict(),
        }
    return {
        "allowed": True,
        "status_code": 200,
        "reason": "tenant_usage_admin_api_allowed",
        "policy": policy.to_dict(),
    }


def summarize_tenant_usage_admin_api(settings: TenantGuardrailsSettings | None = None) -> dict[str, object]:
    active = settings or TenantGuardrailsSettings()
    policy = tenant_usage_admin_policy_from_settings(active)
    return {
        "tenant_usage_admin_api_version": MODULE_27_TENANT_USAGE_ADMIN_API_VERSION,
        "enabled": policy.enabled,
        "read_only": policy.read_only,
        "admin_header": policy.admin_header,
        "admin_keys_configured": bool(policy.accepted_admin_keys),
        "tenant_usage_ledger_version": MODULE_24_TENANT_USAGE_LEDGER_VERSION,
        "tenant_usage_ledger_storage_version": MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not policy.enabled,
        "external_storage_enabled": policy.external_storage_enabled,
        "live_external_action_enabled": policy.live_external_action_enabled,
        "billing_provider_integrated": policy.billing_provider_integrated,
        "payment_processing_enabled": policy.payment_processing_enabled,
    }


@router.get("/tenant-usage")
def read_tenant_usage(
    request: Request,
    tenant_id: str = Query(min_length=1, max_length=MAX_TENANT_ID_LENGTH),
    period: str | None = Query(default=None, max_length=MAX_PERIOD_LENGTH),
    x_oris_admin_key: str | None = Header(default=None),
) -> dict[str, object]:
    settings = load_product_settings()
    policy = tenant_usage_admin_policy_from_settings(settings.tenant_guardrails)
    headers = dict(request.headers)
    if x_oris_admin_key is not None and policy.admin_header.lower() != "x-oris-admin-key":
        headers["x-oris-admin-key"] = x_oris_admin_key
    access = evaluate_tenant_usage_admin_access(headers, policy)
    if not access["allowed"]:
        raise HTTPException(status_code=int(access["status_code"]), detail=access)

    cleaned_tenant_id = _sanitize_tenant_id(tenant_id)
    cleaned_period = _sanitize_period(period)
    ledger = build_tenant_usage_ledger(settings.tenant_guardrails)
    usage = ledger.get_usage(cleaned_tenant_id, period=cleaned_period)
    return {
        "tenant_usage_admin_api_version": MODULE_27_TENANT_USAGE_ADMIN_API_VERSION,
        "read_only": True,
        "reason": access["reason"],
        "tenant_id": usage.tenant_id,
        "period": usage.period,
        "usage": usage.to_dict(),
        "storage": summarize_tenant_usage_ledger(ledger=ledger, settings=settings.tenant_guardrails),
        "policy": policy.to_dict(),
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
        "billing_provider_integrated": settings.tenant_guardrails.billing_provider_integrated,
        "payment_processing_enabled": settings.tenant_guardrails.payment_processing_enabled,
    }
