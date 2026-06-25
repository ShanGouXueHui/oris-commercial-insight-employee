from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Protocol

from app.tenant_entitlements import TenantEntitlementRecord, UsageRecord, evaluate_entitlement

MODULE_24_TENANT_USAGE_LEDGER_VERSION = "2026-06-25-module-24"
MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION = "2026-06-25-module-26"
SQLITE_TENANT_USAGE_TABLES = ("tenant_usage_metadata", "tenant_usage")
SQLITE_TENANT_USAGE_LEDGER_MODES = {"sqlite", "sqlite_durable", "durable_sqlite"}
DEFAULT_TENANT_USAGE_LEDGER_PATH = "reports/tenant_usage/tenant_usage_ledger.sqlite3"


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


class SQLiteTenantUsageLedger:
    """Durable local tenant usage ledger backed by SQLite."""

    def __init__(self, db_path: str, schema_version: str = MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION) -> None:
        self.db_path = db_path
        self.schema_version = schema_version
        self.initialize_schema()

    def initialize_schema(self) -> None:
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_usage_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_usage (
                    tenant_id TEXT NOT NULL,
                    period TEXT NOT NULL,
                    request_count INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, period)
                )
                """
            )
            now = _utc_now().isoformat()
            conn.execute(
                """
                INSERT INTO tenant_usage_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                ("schema_version", self.schema_version, now),
            )
            conn.execute(
                """
                INSERT INTO tenant_usage_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                ("ledger_type", "sqlite", now),
            )

    def get_usage(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> UsageRecord:
        active_period = period or monthly_period(now)
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT request_count, updated_at
                FROM tenant_usage
                WHERE tenant_id = ? AND period = ?
                """,
                (tenant_id, active_period),
            ).fetchone()
        if not row:
            return UsageRecord(
                tenant_id=tenant_id,
                period=active_period,
                request_count=0,
                updated_at=_utc_now().isoformat(),
            )
        return UsageRecord(
            tenant_id=tenant_id,
            period=active_period,
            request_count=int(row[0]),
            updated_at=str(row[1]),
        )

    def consume(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> UsageRecord:
        active_period = period or monthly_period(now)
        updated_at = _utc_now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tenant_usage (tenant_id, period, request_count, updated_at)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(tenant_id, period)
                DO UPDATE SET request_count = request_count + 1, updated_at = excluded.updated_at
                """,
                (tenant_id, active_period, updated_at),
            )
            row = conn.execute(
                """
                SELECT request_count, updated_at
                FROM tenant_usage
                WHERE tenant_id = ? AND period = ?
                """,
                (tenant_id, active_period),
            ).fetchone()
        return UsageRecord(
            tenant_id=tenant_id,
            period=active_period,
            request_count=int(row[0]) if row else 0,
            updated_at=str(row[1]) if row else updated_at,
        )

    def snapshot(self, tenant_id: str, period: str | None = None, now: datetime | None = None) -> TenantUsageSnapshot:
        usage = self.get_usage(tenant_id, period=period, now=now)
        return TenantUsageSnapshot(tenant_id=usage.tenant_id, period=usage.period, request_count=usage.request_count)

    def count_rows(self, table_name: str) -> int:
        if table_name not in SQLITE_TENANT_USAGE_TABLES:
            raise ValueError(f"unsupported tenant usage ledger table: {table_name}")
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            return int(row[0]) if row else 0

    def load_usage_rows(self, tenant_id: str | None = None) -> list[dict[str, object]]:
        query = """
            SELECT tenant_id, period, request_count, updated_at
            FROM tenant_usage
        """
        params: tuple[str, ...] = ()
        if tenant_id is not None:
            query += " WHERE tenant_id = ?"
            params = (tenant_id,)
        query += " ORDER BY tenant_id, period"
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            {
                "tenant_id": row[0],
                "period": row[1],
                "request_count": int(row[2]),
                "updated_at": row[3],
            }
            for row in rows
        ]


DEFAULT_TENANT_USAGE_LEDGER = InMemoryTenantUsageLedger()


def reset_default_tenant_usage_ledger() -> None:
    DEFAULT_TENANT_USAGE_LEDGER.clear()


def _setting_value(settings: object | None, key: str, default: str) -> str:
    if settings is not None and hasattr(settings, key):
        value = getattr(settings, key)
        return str(value) if value is not None else default
    return default


def build_tenant_usage_ledger(
    settings: object | None = None,
    env: Mapping[str, str] | None = None,
) -> TenantUsageLedger:
    values = os.environ if env is None else env
    storage_mode = values.get(
        "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE",
        _setting_value(settings, "tenant_usage_ledger_storage", "in_memory"),
    ).strip().lower()
    if storage_mode in SQLITE_TENANT_USAGE_LEDGER_MODES:
        return SQLiteTenantUsageLedger(
            values.get(
                "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH",
                _setting_value(settings, "tenant_usage_ledger_path", DEFAULT_TENANT_USAGE_LEDGER_PATH),
            ),
            values.get(
                "ORIS_INSIGHT_TENANT_USAGE_LEDGER_SCHEMA_VERSION",
                _setting_value(
                    settings,
                    "tenant_usage_ledger_schema_version",
                    MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION,
                ),
            ),
        )
    return DEFAULT_TENANT_USAGE_LEDGER


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


def summarize_tenant_usage_ledger(
    ledger: TenantUsageLedger | None = None,
    settings: object | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    configured_storage_mode = values.get(
        "ORIS_INSIGHT_TENANT_USAGE_LEDGER_STORAGE",
        _setting_value(settings, "tenant_usage_ledger_storage", "in_memory"),
    ).strip().lower()
    storage_mode = "sqlite" if configured_storage_mode in SQLITE_TENANT_USAGE_LEDGER_MODES else "in_memory"
    active_ledger = ledger
    if active_ledger is None and configured_storage_mode in SQLITE_TENANT_USAGE_LEDGER_MODES:
        active_ledger = build_tenant_usage_ledger(settings=settings, env=values)
    ledger_type = "custom"
    if active_ledger is None or isinstance(active_ledger, InMemoryTenantUsageLedger):
        ledger_type = "in_memory"
    elif isinstance(active_ledger, SQLiteTenantUsageLedger):
        ledger_type = "sqlite"
    return {
        "tenant_usage_ledger_version": MODULE_24_TENANT_USAGE_LEDGER_VERSION,
        "tenant_usage_ledger_storage_version": MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION,
        "ledger_type": ledger_type,
        "storage_mode": storage_mode,
        "durable_store": "sqlite" if storage_mode == "sqlite" else None,
        "local_path": values.get(
            "ORIS_INSIGHT_TENANT_USAGE_LEDGER_PATH",
            _setting_value(settings, "tenant_usage_ledger_path", DEFAULT_TENANT_USAGE_LEDGER_PATH),
        )
        if storage_mode == "sqlite"
        else None,
        "schema_version": values.get(
            "ORIS_INSIGHT_TENANT_USAGE_LEDGER_SCHEMA_VERSION",
            _setting_value(settings, "tenant_usage_ledger_schema_version", MODULE_26_TENANT_USAGE_LEDGER_STORAGE_VERSION),
        ),
        "tables": list(SQLITE_TENANT_USAGE_TABLES) if storage_mode == "sqlite" else [],
        "monthly_period_supported": True,
        "consume_supported": True,
        "snapshot_supported": True,
        "durable_storage_ready": storage_mode == "sqlite",
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
        "supported_storage_modes": ["in_memory", "sqlite"],
    }
