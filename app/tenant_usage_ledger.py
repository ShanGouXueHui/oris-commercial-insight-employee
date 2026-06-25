from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from app.tenant_entitlements import TenantEntitlementRecord, UsageRecord, evaluate_entitlement

MODULE_24_TENANT_USAGE_LEDGER_VERSION = "2026-06-25-module-24"


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def monthly_period(now: datetime | None = None) -> str:
    active_now = now or _utc_now()
    return active_now.strftime("%Y-%m")


class TenantUsageLedger(Protocol):
    def get_usage(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> UsageRecord:
        ...

    def consume(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> UsageRecord:
        ...


@dataclass(frozen=True)
class TenantUsageSnapshot:
    tenant_id: str
    period: str
    request_count: int
    ledger_version: str = MODULE_24_TENANT_USAGE_LEDGER_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "tenant_id": self.tenant_id,
            "period": self.period,
            "request_count": self.request_count,
            "ledger_version": self.ledger_version,
        }


class InMemoryTenantUsageLedger:
    def __init__(self) -> None:
        self._counts: dict[tuple[str, str], int] = {}

    def clear(self) -> None:
        self._counts.clear()

    def get_usage(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> UsageRecord:
        active_period = period or monthly_period(now)
        count = self._counts.get((tenant_id, active_period), 0)
        return UsageRecord(tenant_id=tenant_id, period=active_period, request_count=count, updated_at=_utc_now().isoformat())

    def consume(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> UsageRecord:
        active_period = period or monthly_period(now)
        key = (tenant_id, active_period)
        self._counts[key] = self._counts.get(key, 0) + 1
        return UsageRecord(
            tenant_id=tenant_id,
            period=active_period,
            request_count=self._counts[key],
            updated_at=_utc_now().isoformat(),
        )

    def snapshot(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> TenantUsageSnapshot:
        usage = self.get_usage(tenant_id, period=period, now=now)
        return TenantUsageSnapshot(tenant_id=usage.tenant_id, period=usage.period, request_count=usage.request_count)


DEFAULT_TENANT_USAGE_LEDGER = InMemoryTenantUsageLedger()


def reset_default_tenant_usage_ledger() -> None:
    DEFAULT_TENANT_USAGE_LEDGER.clear()


def evaluate_entitlement_against_usage_ledger(
    tenant_id: str,
    entitlements: tuple[TenantEntitlementRecord, ...],
    ledger: TenantUsageLedger | None = None,
    period: str | None = None,
    now: datetime | None = None,
):
    active_ledger = ledger or DEFAULT_TENANT_USAGE_LEDGER
    usage = active_ledger.get_usage(tenant_id, period=period, now=now)
    return evaluate_entitlement(tenant_id, entitlements, usage)


def summarize_tenant_usage_ledger(ledger: TenantUsageLedger | None = None) -> dict[str, object]:
    return {
        "tenant_usage_ledger_version": MODULE_24_TENANT_USAGE_LEDGER_VERSION,
        "ledger_type": "in_memory" if ledger is None or isinstance(ledger, InMemoryTenantUsageLedger) else "custom",
        "monthly_period_supported": True,
        "consume_supported": True,
        "snapshot_supported": True,
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
    }
