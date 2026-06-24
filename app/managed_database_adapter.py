from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Mapping, Protocol

from app.managed_database import build_postgres_schema_manifest, summarize_managed_database_transition

MODULE_14_MANAGED_DB_ADAPTER_VERSION = "2026-06-24-module-14"
DISABLED_MODES = {"disabled", "off", "sqlite_local"}
POSTGRES_BOUNDARY_MODES = {"postgres_boundary", "postgresql_boundary", "managed_postgres_boundary"}


@dataclass(frozen=True)
class ManagedDatabaseAdapterSettings:
    mode: str = "disabled"
    target: str = "postgresql"
    live_connection_enabled: bool = False
    credential_configured: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ManagedDatabaseReadiness:
    ready: bool
    adapter_version: str
    mode: str
    target: str
    credential_configured: bool
    credential_exposed: bool
    live_connection_enabled: bool
    live_connection_attempted: bool
    live_connection_required: bool
    reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class ManagedDatabaseAdapter(Protocol):
    def readiness(self) -> ManagedDatabaseReadiness:
        ...

    def migration_preview(self) -> dict[str, object]:
        ...


class DisabledManagedDatabaseAdapter:
    def __init__(self, settings: ManagedDatabaseAdapterSettings) -> None:
        self.settings = settings

    def readiness(self) -> ManagedDatabaseReadiness:
        return ManagedDatabaseReadiness(
            ready=True,
            adapter_version=MODULE_14_MANAGED_DB_ADAPTER_VERSION,
            mode=self.settings.mode,
            target=self.settings.target,
            credential_configured=self.settings.credential_configured,
            credential_exposed=False,
            live_connection_enabled=False,
            live_connection_attempted=False,
            live_connection_required=False,
            reason="managed_database_adapter_disabled_sqlite_runtime_active",
        )

    def migration_preview(self) -> dict[str, object]:
        manifest = build_postgres_schema_manifest()
        return {
            "adapter_version": MODULE_14_MANAGED_DB_ADAPTER_VERSION,
            "mode": self.settings.mode,
            "target": self.settings.target,
            "preview_only": True,
            "live_connection_attempted": False,
            "manifest": manifest,
        }


class PostgresBoundaryManagedDatabaseAdapter:
    def __init__(self, settings: ManagedDatabaseAdapterSettings) -> None:
        self.settings = settings

    def readiness(self) -> ManagedDatabaseReadiness:
        if not self.settings.credential_configured:
            reason = "managed_database_credential_missing"
            ready = False
        elif not self.settings.live_connection_enabled:
            reason = "managed_database_configured_but_live_connection_disabled"
            ready = True
        else:
            reason = "managed_database_live_connection_not_implemented"
            ready = False
        return ManagedDatabaseReadiness(
            ready=ready,
            adapter_version=MODULE_14_MANAGED_DB_ADAPTER_VERSION,
            mode=self.settings.mode,
            target=self.settings.target,
            credential_configured=self.settings.credential_configured,
            credential_exposed=False,
            live_connection_enabled=self.settings.live_connection_enabled,
            live_connection_attempted=False,
            live_connection_required=False,
            reason=reason,
        )

    def migration_preview(self) -> dict[str, object]:
        manifest = build_postgres_schema_manifest()
        return {
            "adapter_version": MODULE_14_MANAGED_DB_ADAPTER_VERSION,
            "mode": self.settings.mode,
            "target": self.settings.target,
            "preview_only": True,
            "credential_configured": self.settings.credential_configured,
            "credential_exposed": False,
            "live_connection_attempted": False,
            "manifest": manifest,
        }


def _bool_from_env(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _credential_configured(env: Mapping[str, str]) -> bool:
    return bool(env.get("ORIS_INSIGHT_DATABASE_URL") or env.get("ORIS_INSIGHT_MANAGED_DB_DSN"))


def load_managed_database_adapter_settings(env: Mapping[str, str] | None = None) -> ManagedDatabaseAdapterSettings:
    values = os.environ if env is None else env
    return ManagedDatabaseAdapterSettings(
        mode=values.get("ORIS_INSIGHT_MANAGED_DB_MODE", "disabled"),
        target=values.get("ORIS_INSIGHT_MANAGED_DB_TARGET", "postgresql"),
        live_connection_enabled=_bool_from_env(values.get("ORIS_INSIGHT_MANAGED_DB_LIVE_CONNECTION_ENABLED"), False),
        credential_configured=_credential_configured(values),
    )


def build_managed_database_adapter(env: Mapping[str, str] | None = None) -> ManagedDatabaseAdapter:
    settings = load_managed_database_adapter_settings(env)
    mode = settings.mode.strip().lower()
    if mode in POSTGRES_BOUNDARY_MODES:
        return PostgresBoundaryManagedDatabaseAdapter(settings)
    return DisabledManagedDatabaseAdapter(settings)


def summarize_managed_database_adapter(env: Mapping[str, str] | None = None) -> dict[str, object]:
    adapter = build_managed_database_adapter(env)
    readiness = adapter.readiness()
    transition = summarize_managed_database_transition()
    return {
        "adapter_version": MODULE_14_MANAGED_DB_ADAPTER_VERSION,
        "readiness": readiness.to_dict(),
        "transition": transition,
        "default_behavior": "sqlite_runtime_active_until_managed_adapter_enabled",
        "credential_exposed": False,
        "live_connection_attempted": False,
        "preview_available": True,
    }
