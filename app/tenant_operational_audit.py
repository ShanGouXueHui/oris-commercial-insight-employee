from __future__ import annotations

import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Protocol

MODULE_28_TENANT_OPERATIONAL_AUDIT_VERSION = "2026-06-25-module-28"
TENANT_OPERATIONAL_AUDIT_TABLES = ("tenant_operational_audit_metadata", "tenant_operational_audit_events")
TENANT_OPERATIONAL_AUDIT_SQLITE_MODES = {"sqlite", "sqlite_durable", "durable_sqlite"}
DEFAULT_TENANT_OPERATIONAL_AUDIT_PATH = "reports/tenant_usage/tenant_operational_audit.sqlite3"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class TenantOperationalAuditEvent:
    event_id: str
    event_type: str
    actor_id: str
    tenant_id: str
    period: str
    operation: str
    result: str
    created_at: str
    audit_version: str = MODULE_28_TENANT_OPERATIONAL_AUDIT_VERSION

    def to_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "tenant_id": self.tenant_id,
            "period": self.period,
            "operation": self.operation,
            "result": self.result,
            "created_at": self.created_at,
            "audit_version": self.audit_version,
        }


class TenantOperationalAuditTrail(Protocol):
    def record_event(
        self,
        event_type: str,
        actor_id: str,
        tenant_id: str,
        period: str,
        operation: str,
        result: str,
    ) -> TenantOperationalAuditEvent:
        ...

    def list_events(self, tenant_id: str | None = None, limit: int = 50) -> list[TenantOperationalAuditEvent]:
        ...


class InMemoryTenantOperationalAuditTrail:
    def __init__(self) -> None:
        self._events: list[TenantOperationalAuditEvent] = []

    def clear(self) -> None:
        self._events.clear()

    def record_event(
        self,
        event_type: str,
        actor_id: str,
        tenant_id: str,
        period: str,
        operation: str,
        result: str,
    ) -> TenantOperationalAuditEvent:
        event = TenantOperationalAuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            actor_id=actor_id,
            tenant_id=tenant_id,
            period=period,
            operation=operation,
            result=result,
            created_at=_utc_now(),
        )
        self._events.append(event)
        return event

    def list_events(self, tenant_id: str | None = None, limit: int = 50) -> list[TenantOperationalAuditEvent]:
        events = [event for event in self._events if tenant_id is None or event.tenant_id == tenant_id]
        return events[-max(limit, 0) :]


class SQLiteTenantOperationalAuditTrail:
    def __init__(self, db_path: str, schema_version: str = MODULE_28_TENANT_OPERATIONAL_AUDIT_VERSION) -> None:
        self.db_path = db_path
        self.schema_version = schema_version
        self.initialize_schema()

    def initialize_schema(self) -> None:
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_operational_audit_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tenant_operational_audit_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    period TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    audit_version TEXT NOT NULL
                )
                """
            )
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO tenant_operational_audit_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                ("schema_version", self.schema_version, now),
            )
            conn.execute(
                """
                INSERT INTO tenant_operational_audit_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                ("trail_type", "sqlite", now),
            )

    def record_event(
        self,
        event_type: str,
        actor_id: str,
        tenant_id: str,
        period: str,
        operation: str,
        result: str,
    ) -> TenantOperationalAuditEvent:
        event = TenantOperationalAuditEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            actor_id=actor_id,
            tenant_id=tenant_id,
            period=period,
            operation=operation,
            result=result,
            created_at=_utc_now(),
            audit_version=self.schema_version,
        )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tenant_operational_audit_events (
                    event_id, event_type, actor_id, tenant_id, period, operation, result, created_at, audit_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.actor_id,
                    event.tenant_id,
                    event.period,
                    event.operation,
                    event.result,
                    event.created_at,
                    event.audit_version,
                ),
            )
        return event

    def list_events(self, tenant_id: str | None = None, limit: int = 50) -> list[TenantOperationalAuditEvent]:
        query = """
            SELECT event_id, event_type, actor_id, tenant_id, period, operation, result, created_at, audit_version
            FROM tenant_operational_audit_events
        """
        params: list[object] = []
        if tenant_id is not None:
            query += " WHERE tenant_id = ?"
            params.append(tenant_id)
        query += " ORDER BY created_at ASC LIMIT ?"
        params.append(max(limit, 0))
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [
            TenantOperationalAuditEvent(
                event_id=row[0],
                event_type=row[1],
                actor_id=row[2],
                tenant_id=row[3],
                period=row[4],
                operation=row[5],
                result=row[6],
                created_at=row[7],
                audit_version=row[8],
            )
            for row in rows
        ]

    def count_rows(self, table_name: str) -> int:
        if table_name not in TENANT_OPERATIONAL_AUDIT_TABLES:
            raise ValueError(f"unsupported tenant operational audit table: {table_name}")
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return int(row[0]) if row else 0


DEFAULT_TENANT_OPERATIONAL_AUDIT_TRAIL = InMemoryTenantOperationalAuditTrail()


def reset_default_tenant_operational_audit_trail() -> None:
    DEFAULT_TENANT_OPERATIONAL_AUDIT_TRAIL.clear()


def _env_bool(values: Mapping[str, str], key: str, default: bool) -> bool:
    raw = values.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _setting_value(settings: object | None, key: str, default: str) -> str:
    if settings is not None and hasattr(settings, key):
        value = getattr(settings, key)
        return str(value) if value is not None else default
    return default


def tenant_operational_audit_enabled(settings: object | None = None, env: Mapping[str, str] | None = None) -> bool:
    values = os.environ if env is None else env
    if "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_ENABLED" in values:
        return _env_bool(values, "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_ENABLED", False)
    if settings is not None and hasattr(settings, "tenant_operational_audit_enabled"):
        return bool(getattr(settings, "tenant_operational_audit_enabled"))
    return False


def build_tenant_operational_audit_trail(
    settings: object | None = None,
    env: Mapping[str, str] | None = None,
) -> TenantOperationalAuditTrail:
    values = os.environ if env is None else env
    storage_mode = values.get(
        "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_STORAGE",
        _setting_value(settings, "tenant_operational_audit_storage", "in_memory"),
    ).strip().lower()
    if storage_mode in TENANT_OPERATIONAL_AUDIT_SQLITE_MODES:
        return SQLiteTenantOperationalAuditTrail(
            values.get(
                "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_PATH",
                _setting_value(settings, "tenant_operational_audit_path", DEFAULT_TENANT_OPERATIONAL_AUDIT_PATH),
            ),
            values.get(
                "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_SCHEMA_VERSION",
                _setting_value(settings, "tenant_operational_audit_schema_version", MODULE_28_TENANT_OPERATIONAL_AUDIT_VERSION),
            ),
        )
    return DEFAULT_TENANT_OPERATIONAL_AUDIT_TRAIL


def summarize_tenant_operational_audit_trail(
    settings: object | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, object]:
    values = os.environ if env is None else env
    configured_storage_mode = values.get(
        "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_STORAGE",
        _setting_value(settings, "tenant_operational_audit_storage", "in_memory"),
    ).strip().lower()
    storage_mode = "sqlite" if configured_storage_mode in TENANT_OPERATIONAL_AUDIT_SQLITE_MODES else "in_memory"
    return {
        "tenant_operational_audit_version": MODULE_28_TENANT_OPERATIONAL_AUDIT_VERSION,
        "enabled": tenant_operational_audit_enabled(settings=settings, env=values),
        "storage_mode": storage_mode,
        "durable_store": "sqlite" if storage_mode == "sqlite" else None,
        "local_path": values.get(
            "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_PATH",
            _setting_value(settings, "tenant_operational_audit_path", DEFAULT_TENANT_OPERATIONAL_AUDIT_PATH),
        )
        if storage_mode == "sqlite"
        else None,
        "schema_version": values.get(
            "ORIS_INSIGHT_TENANT_OPERATIONAL_AUDIT_SCHEMA_VERSION",
            _setting_value(settings, "tenant_operational_audit_schema_version", MODULE_28_TENANT_OPERATIONAL_AUDIT_VERSION),
        ),
        "tables": list(TENANT_OPERATIONAL_AUDIT_TABLES) if storage_mode == "sqlite" else [],
        "read_only_observability": True,
        "explicit_configuration_required": True,
        "request_path_unchanged_by_default": not tenant_operational_audit_enabled(settings=settings, env=values),
        "external_storage_enabled": False,
        "live_external_action_enabled": False,
        "billing_provider_integrated": False,
        "payment_processing_enabled": False,
        "supported_storage_modes": ["in_memory", "sqlite"],
    }
