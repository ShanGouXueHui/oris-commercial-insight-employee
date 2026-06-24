from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

MODULE_13_MANAGED_DB_PLAN_VERSION = "2026-06-24-module-13"
SUPPORTED_MANAGED_DB_TARGETS = ("postgresql",)


@dataclass(frozen=True)
class ManagedDatabaseColumn:
    name: str
    sqlite_type: str
    postgres_type: str
    nullable: bool = False
    primary_key: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ManagedDatabaseTable:
    name: str
    purpose: str
    columns: tuple[ManagedDatabaseColumn, ...]
    source_module: str

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "source_module": self.source_module,
            "columns": [column.to_dict() for column in self.columns],
        }


EVIDENCE_TABLES: tuple[ManagedDatabaseTable, ...] = (
    ManagedDatabaseTable(
        name="persistence_metadata",
        purpose="Evidence store metadata and schema version tracking.",
        source_module="module_8",
        columns=(
            ManagedDatabaseColumn("key", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("value", "TEXT", "TEXT"),
            ManagedDatabaseColumn("updated_at", "TEXT", "TIMESTAMPTZ"),
        ),
    ),
    ManagedDatabaseTable(
        name="runtime_runs",
        purpose="Runtime run headers for persisted evidence packets.",
        source_module="module_8",
        columns=(
            ManagedDatabaseColumn("runtime_run_id", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("subject_company", "TEXT", "TEXT"),
            ManagedDatabaseColumn("storage_mode", "TEXT", "TEXT"),
            ManagedDatabaseColumn("persisted_at", "TEXT", "TIMESTAMPTZ"),
            ManagedDatabaseColumn("schema_version", "TEXT", "TEXT"),
            ManagedDatabaseColumn("source_count", "INTEGER", "INTEGER"),
            ManagedDatabaseColumn("evidence_count", "INTEGER", "INTEGER"),
            ManagedDatabaseColumn("validation_error_count", "INTEGER", "INTEGER"),
        ),
    ),
    ManagedDatabaseTable(
        name="evidence_sources",
        purpose="Source records linked to a runtime run.",
        source_module="module_8",
        columns=(
            ManagedDatabaseColumn("runtime_run_id", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("source_id", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("source_type", "TEXT", "TEXT"),
            ManagedDatabaseColumn("title", "TEXT", "TEXT"),
            ManagedDatabaseColumn("credibility_score", "REAL", "DOUBLE PRECISION"),
            ManagedDatabaseColumn("url", "TEXT", "TEXT", nullable=True),
        ),
    ),
    ManagedDatabaseTable(
        name="evidence_items",
        purpose="Evidence claims linked to sources and runtime runs.",
        source_module="module_8",
        columns=(
            ManagedDatabaseColumn("runtime_run_id", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("evidence_id", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("source_id", "TEXT", "TEXT"),
            ManagedDatabaseColumn("lens", "TEXT", "TEXT"),
            ManagedDatabaseColumn("claim", "TEXT", "TEXT"),
            ManagedDatabaseColumn("relevance_score", "REAL", "DOUBLE PRECISION"),
        ),
    ),
)

GUARDRAIL_TABLES: tuple[ManagedDatabaseTable, ...] = (
    ManagedDatabaseTable(
        name="guardrail_metadata",
        purpose="Commercial guardrail ledger metadata and schema version tracking.",
        source_module="module_11",
        columns=(
            ManagedDatabaseColumn("key", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("value", "TEXT", "TEXT"),
            ManagedDatabaseColumn("updated_at", "TEXT", "TIMESTAMPTZ"),
        ),
    ),
    ManagedDatabaseTable(
        name="guardrail_usage",
        purpose="Per-client quota and rate-limit bucket counters.",
        source_module="module_11",
        columns=(
            ManagedDatabaseColumn("client_id", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("scope", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("bucket", "TEXT", "TEXT", primary_key=True),
            ManagedDatabaseColumn("request_count", "INTEGER", "INTEGER"),
            ManagedDatabaseColumn("updated_at", "TEXT", "TIMESTAMPTZ"),
        ),
    ),
)


def managed_database_tables() -> tuple[ManagedDatabaseTable, ...]:
    return EVIDENCE_TABLES + GUARDRAIL_TABLES


def table_names(tables: Iterable[ManagedDatabaseTable] | None = None) -> list[str]:
    active_tables = tuple(tables or managed_database_tables())
    return [table.name for table in active_tables]


def _primary_key_clause(table: ManagedDatabaseTable) -> str:
    keys = [column.name for column in table.columns if column.primary_key]
    if not keys:
        return ""
    return f", PRIMARY KEY ({', '.join(keys)})"


def render_postgres_create_table(table: ManagedDatabaseTable) -> str:
    column_sql = []
    for column in table.columns:
        nullable = "" if not column.nullable else " NULL"
        not_null = " NOT NULL" if not column.nullable else ""
        column_sql.append(f"{column.name} {column.postgres_type}{nullable or not_null}")
    body = ", ".join(column_sql) + _primary_key_clause(table)
    return f"CREATE TABLE IF NOT EXISTS {table.name} ({body});"


def build_postgres_schema_manifest() -> dict[str, object]:
    tables = managed_database_tables()
    return {
        "plan_version": MODULE_13_MANAGED_DB_PLAN_VERSION,
        "target": "postgresql",
        "default_runtime_store": "sqlite_until_managed_db_enabled",
        "live_connection_required": False,
        "tables": [table.to_dict() for table in tables],
        "table_names": table_names(tables),
        "create_table_statements": [render_postgres_create_table(table) for table in tables],
        "migration_order": table_names(tables),
        "non_scope": ["live_database_connection", "data_backfill_execution", "production_cutover"],
    }


def summarize_managed_database_transition() -> dict[str, object]:
    manifest = build_postgres_schema_manifest()
    return {
        "plan_version": MODULE_13_MANAGED_DB_PLAN_VERSION,
        "supported_targets": list(SUPPORTED_MANAGED_DB_TARGETS),
        "target": manifest["target"],
        "table_count": len(manifest["table_names"]),
        "table_names": manifest["table_names"],
        "live_connection_required": False,
        "production_cutover_ready": False,
        "default_behavior": "sqlite_local_until_managed_db_enabled",
    }
