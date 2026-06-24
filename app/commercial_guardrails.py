from __future__ import annotations

import hashlib
import os
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Protocol

from app.config import CommercialGuardrailsSettings

MODULE_10_GUARDRAIL_POLICY_VERSION = "2026-06-24-module-10"
MODULE_11_GUARDRAIL_LEDGER_SCHEMA_VERSION = "2026-06-24-module-11"
SQLITE_GUARDRAIL_TABLES = ("guardrail_metadata", "guardrail_usage")
BLOCKING_MODES = {"blocking", "enforce", "enforced"}
OBSERVE_MODES = {"observe", "monitor", "disabled", "off"}
SQLITE_LEDGER_MODES = {"sqlite", "sqlite_durable", "durable_sqlite"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class GuardrailLedger(Protocol):
    def consume(self, client_id: str, now: datetime | None = None) -> tuple[int, int]:
        ...


@dataclass(frozen=True)
class GuardrailErrorPayload:
    error_code: str
    message: str
    status_code: int
    policy_version: str = MODULE_10_GUARDRAIL_POLICY_VERSION

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    status_code: int
    client_id: str
    enforcement_mode: str
    policy_version: str
    reason: str
    remaining_minute: int | None = None
    remaining_day: int | None = None
    retry_after_seconds: int | None = None
    error: GuardrailErrorPayload | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": self.allowed,
            "status_code": self.status_code,
            "client_id": self.client_id,
            "enforcement_mode": self.enforcement_mode,
            "policy_version": self.policy_version,
            "reason": self.reason,
            "remaining_minute": self.remaining_minute,
            "remaining_day": self.remaining_day,
            "retry_after_seconds": self.retry_after_seconds,
            "error": self.error.to_dict() if self.error else None,
        }


class InMemoryGuardrailLedger:
    """Small deterministic ledger for local API guardrail enforcement and tests."""

    def __init__(self) -> None:
        self.minute_counts: dict[tuple[str, str], int] = {}
        self.day_counts: dict[tuple[str, str], int] = {}

    def clear(self) -> None:
        self.minute_counts.clear()
        self.day_counts.clear()

    def consume(self, client_id: str, now: datetime | None = None) -> tuple[int, int]:
        active_now = now or _utc_now()
        minute_bucket = active_now.strftime("%Y-%m-%dT%H:%M")
        day_bucket = active_now.strftime("%Y-%m-%d")
        minute_key = (client_id, minute_bucket)
        day_key = (client_id, day_bucket)
        self.minute_counts[minute_key] = self.minute_counts.get(minute_key, 0) + 1
        self.day_counts[day_key] = self.day_counts.get(day_key, 0) + 1
        return self.minute_counts[minute_key], self.day_counts[day_key]


class SQLiteGuardrailLedger:
    """Durable local guardrail ledger for quota and rate-limit counters."""

    def __init__(self, db_path: str, schema_version: str = MODULE_11_GUARDRAIL_LEDGER_SCHEMA_VERSION) -> None:
        self.db_path = db_path
        self.schema_version = schema_version
        self.initialize_schema()

    def initialize_schema(self) -> None:
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guardrail_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guardrail_usage (
                    client_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    bucket TEXT NOT NULL,
                    request_count INTEGER NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (client_id, scope, bucket)
                )
                """
            )
            now = _utc_now().isoformat()
            conn.execute(
                """
                INSERT INTO guardrail_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                ("schema_version", self.schema_version, now),
            )
            conn.execute(
                """
                INSERT INTO guardrail_metadata (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
                """,
                ("ledger_type", "sqlite", now),
            )

    def consume(self, client_id: str, now: datetime | None = None) -> tuple[int, int]:
        active_now = now or _utc_now()
        minute_bucket = active_now.strftime("%Y-%m-%dT%H:%M")
        day_bucket = active_now.strftime("%Y-%m-%d")
        updated_at = active_now.isoformat()
        with sqlite3.connect(self.db_path) as conn:
            minute_count = self._increment(conn, client_id, "minute", minute_bucket, updated_at)
            day_count = self._increment(conn, client_id, "day", day_bucket, updated_at)
            return minute_count, day_count

    def _increment(self, conn: sqlite3.Connection, client_id: str, scope: str, bucket: str, updated_at: str) -> int:
        conn.execute(
            """
            INSERT INTO guardrail_usage (client_id, scope, bucket, request_count, updated_at)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(client_id, scope, bucket)
            DO UPDATE SET request_count = request_count + 1, updated_at = excluded.updated_at
            """,
            (client_id, scope, bucket, updated_at),
        )
        row = conn.execute(
            "SELECT request_count FROM guardrail_usage WHERE client_id = ? AND scope = ? AND bucket = ?",
            (client_id, scope, bucket),
        ).fetchone()
        return int(row[0]) if row else 0

    def count_rows(self, table_name: str) -> int:
        if table_name not in SQLITE_GUARDRAIL_TABLES:
            raise ValueError(f"unsupported guardrail ledger table: {table_name}")
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
            return int(row[0]) if row else 0

    def load_usage_rows(self, client_id: str) -> list[dict[str, object]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT client_id, scope, bucket, request_count, updated_at
                FROM guardrail_usage
                WHERE client_id = ?
                ORDER BY scope, bucket
                """,
                (client_id,),
            ).fetchall()
        return [
            {
                "client_id": row[0],
                "scope": row[1],
                "bucket": row[2],
                "request_count": int(row[3]),
                "updated_at": row[4],
            }
            for row in rows
        ]


DEFAULT_GUARDRAIL_LEDGER = InMemoryGuardrailLedger()


def reset_default_guardrail_ledger() -> None:
    DEFAULT_GUARDRAIL_LEDGER.clear()


def build_guardrail_ledger(env: Mapping[str, str] | None = None) -> GuardrailLedger:
    values = os.environ if env is None else env
    storage_mode = values.get("ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE", "in_memory").strip().lower()
    if storage_mode in SQLITE_LEDGER_MODES:
        return SQLiteGuardrailLedger(
            values.get("ORIS_INSIGHT_GUARDRAIL_LEDGER_PATH", "reports/guardrails/guardrail_ledger.sqlite3"),
            values.get("ORIS_INSIGHT_GUARDRAIL_LEDGER_SCHEMA_VERSION", MODULE_11_GUARDRAIL_LEDGER_SCHEMA_VERSION),
        )
    return DEFAULT_GUARDRAIL_LEDGER


def summarize_guardrail_ledger(env: Mapping[str, str] | None = None) -> dict[str, object]:
    values = os.environ if env is None else env
    storage_mode = values.get("ORIS_INSIGHT_GUARDRAIL_LEDGER_STORAGE", "in_memory").strip().lower()
    local_path = values.get("ORIS_INSIGHT_GUARDRAIL_LEDGER_PATH", "reports/guardrails/guardrail_ledger.sqlite3")
    schema_version = values.get("ORIS_INSIGHT_GUARDRAIL_LEDGER_SCHEMA_VERSION", MODULE_11_GUARDRAIL_LEDGER_SCHEMA_VERSION)
    return {
        "schema_version": schema_version,
        "storage_mode": "sqlite" if storage_mode in SQLITE_LEDGER_MODES else "in_memory",
        "durable_store": "sqlite" if storage_mode in SQLITE_LEDGER_MODES else None,
        "local_path": local_path if storage_mode in SQLITE_LEDGER_MODES else None,
        "tables": list(SQLITE_GUARDRAIL_TABLES) if storage_mode in SQLITE_LEDGER_MODES else [],
        "persistent_quota_ready": storage_mode in SQLITE_LEDGER_MODES,
        "supported_storage_modes": ["in_memory", "sqlite"],
    }


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:12]


def _header_get(headers: Mapping[str, str], name: str) -> str | None:
    lower_name = name.lower()
    for key, value in headers.items():
        if key.lower() == lower_name:
            return value
    return None


def _is_exempt_path(path: str, settings: CommercialGuardrailsSettings) -> bool:
    return path in settings.exempt_paths or any(path.startswith(f"{prefix}/") for prefix in settings.exempt_paths)


def _client_id_from_headers(headers: Mapping[str, str], settings: CommercialGuardrailsSettings) -> str:
    api_key = _header_get(headers, "x-api-key")
    if api_key:
        return f"api-key:{_hash_key(api_key)}"
    explicit_client = _header_get(headers, "x-client-id")
    if explicit_client:
        return explicit_client[:80]
    return settings.default_client_id


def summarize_guardrail_policy(settings: CommercialGuardrailsSettings) -> dict[str, object]:
    return {
        "policy_version": MODULE_10_GUARDRAIL_POLICY_VERSION,
        "enforcement_mode": settings.enforcement_mode,
        "require_api_key": settings.require_api_key,
        "api_keys_configured": bool(settings.accepted_api_keys),
        "rate_limit_per_minute": settings.rate_limit_per_minute,
        "quota_per_day": settings.quota_per_day,
        "error_policy": settings.error_policy,
        "exempt_paths": list(settings.exempt_paths),
        "default_behavior": "observe_non_blocking" if settings.enforcement_mode in OBSERVE_MODES else "blocking_when_configured",
        "ledger": summarize_guardrail_ledger(),
    }


def evaluate_guardrails(
    path: str,
    method: str,
    headers: Mapping[str, str],
    settings: CommercialGuardrailsSettings,
    ledger: GuardrailLedger | None = None,
    now: datetime | None = None,
) -> GuardrailDecision:
    active_ledger = ledger or build_guardrail_ledger()
    client_id = _client_id_from_headers(headers, settings)
    enforcement_mode = settings.enforcement_mode.strip().lower()

    if _is_exempt_path(path, settings):
        return GuardrailDecision(
            allowed=True,
            status_code=200,
            client_id=client_id,
            enforcement_mode=enforcement_mode,
            policy_version=MODULE_10_GUARDRAIL_POLICY_VERSION,
            reason="exempt_path",
        )

    if enforcement_mode in OBSERVE_MODES:
        return GuardrailDecision(
            allowed=True,
            status_code=200,
            client_id=client_id,
            enforcement_mode=enforcement_mode,
            policy_version=MODULE_10_GUARDRAIL_POLICY_VERSION,
            reason="observe_mode_non_blocking",
        )

    if enforcement_mode not in BLOCKING_MODES:
        return GuardrailDecision(
            allowed=True,
            status_code=200,
            client_id=client_id,
            enforcement_mode=enforcement_mode,
            policy_version=MODULE_10_GUARDRAIL_POLICY_VERSION,
            reason="unknown_mode_fails_open",
        )

    api_key = _header_get(headers, "x-api-key")
    if settings.require_api_key and not api_key:
        return _blocked(client_id, enforcement_mode, 401, "api_key_missing", "Missing required x-api-key header.")
    if settings.require_api_key and api_key not in settings.accepted_api_keys:
        return _blocked(client_id, enforcement_mode, 401, "api_key_invalid", "Invalid x-api-key header.")

    minute_count, day_count = active_ledger.consume(client_id, now=now)
    remaining_minute = max(settings.rate_limit_per_minute - minute_count, 0)
    remaining_day = max(settings.quota_per_day - day_count, 0)
    if minute_count > settings.rate_limit_per_minute:
        return _blocked(
            client_id,
            enforcement_mode,
            429,
            "rate_limit_exceeded",
            "Per-minute request limit exceeded.",
            remaining_minute=0,
            remaining_day=remaining_day,
            retry_after_seconds=60,
        )
    if day_count > settings.quota_per_day:
        return _blocked(
            client_id,
            enforcement_mode,
            429,
            "quota_exceeded",
            "Daily quota exceeded.",
            remaining_minute=remaining_minute,
            remaining_day=0,
            retry_after_seconds=3600,
        )
    return GuardrailDecision(
        allowed=True,
        status_code=200,
        client_id=client_id,
        enforcement_mode=enforcement_mode,
        policy_version=MODULE_10_GUARDRAIL_POLICY_VERSION,
        reason="allowed",
        remaining_minute=remaining_minute,
        remaining_day=remaining_day,
    )


def _blocked(
    client_id: str,
    enforcement_mode: str,
    status_code: int,
    error_code: str,
    message: str,
    remaining_minute: int | None = None,
    remaining_day: int | None = None,
    retry_after_seconds: int | None = None,
) -> GuardrailDecision:
    return GuardrailDecision(
        allowed=False,
        status_code=status_code,
        client_id=client_id,
        enforcement_mode=enforcement_mode,
        policy_version=MODULE_10_GUARDRAIL_POLICY_VERSION,
        reason=error_code,
        remaining_minute=remaining_minute,
        remaining_day=remaining_day,
        retry_after_seconds=retry_after_seconds,
        error=GuardrailErrorPayload(error_code=error_code, message=message, status_code=status_code),
    )
