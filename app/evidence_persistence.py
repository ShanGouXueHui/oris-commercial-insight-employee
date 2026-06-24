from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Protocol

from app.config import EvidencePersistenceSettings, MODULE_8_EVIDENCE_SCHEMA_VERSION
from app.evidence_ingestion import IngestionResult

SQLITE_EVIDENCE_TABLES = (
    "persistence_metadata",
    "runtime_runs",
    "evidence_sources",
    "evidence_items",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EvidencePersistenceRecord:
    runtime_run_id: str
    subject_company: str
    storage_mode: str
    persisted_at: str
    source_ids: list[str]
    evidence_ids: list[str]
    path: str | None = None
    schema_version: str = MODULE_8_EVIDENCE_SCHEMA_VERSION
    source_count: int = 0
    evidence_count: int = 0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class EvidenceStore(Protocol):
    def persist(self, runtime_run_id: str, ingestion: IngestionResult) -> EvidencePersistenceRecord:
        """Persist or index evidence produced by a Runtime v2 run."""


class InMemoryEvidenceStore:
    def __init__(self) -> None:
        self.records: dict[str, EvidencePersistenceRecord] = {}

    def persist(self, runtime_run_id: str, ingestion: IngestionResult) -> EvidencePersistenceRecord:
        record = _build_record(runtime_run_id, ingestion, storage_mode="in_memory", path=None)
        self.records[runtime_run_id] = record
        return record


class FileSystemEvidenceStore:
    def __init__(self, root_path: str) -> None:
        self.root_path = Path(root_path)

    def persist(self, runtime_run_id: str, ingestion: IngestionResult) -> EvidencePersistenceRecord:
        self.root_path.mkdir(parents=True, exist_ok=True)
        path = self.root_path / f"{runtime_run_id}.json"
        payload = {
            "runtime_run_id": runtime_run_id,
            "ingestion": ingestion.to_dict(),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return _build_record(runtime_run_id, ingestion, storage_mode="filesystem", path=str(path))


class SQLiteEvidenceStore:
    """Durable, dependency-free evidence store for local and deployment smoke validation."""

    def __init__(self, database_path: str, schema_version: str = MODULE_8_EVIDENCE_SCHEMA_VERSION) -> None:
        self.database_path = database_path
        self.schema_version = schema_version
        if database_path != ":memory:":
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def initialize_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS persistence_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_runs (
                    runtime_run_id TEXT PRIMARY KEY,
                    subject_company TEXT NOT NULL,
                    storage_mode TEXT NOT NULL,
                    persisted_at TEXT NOT NULL,
                    schema_version TEXT NOT NULL,
                    source_count INTEGER NOT NULL,
                    evidence_count INTEGER NOT NULL,
                    validation_error_count INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_sources (
                    runtime_run_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    credibility_score REAL NOT NULL,
                    url TEXT,
                    PRIMARY KEY (runtime_run_id, source_id),
                    FOREIGN KEY (runtime_run_id) REFERENCES runtime_runs(runtime_run_id) ON DELETE CASCADE
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS evidence_items (
                    runtime_run_id TEXT NOT NULL,
                    evidence_id TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    lens TEXT NOT NULL,
                    claim TEXT NOT NULL,
                    relevance_score REAL NOT NULL,
                    PRIMARY KEY (runtime_run_id, evidence_id),
                    FOREIGN KEY (runtime_run_id) REFERENCES runtime_runs(runtime_run_id) ON DELETE CASCADE,
                    FOREIGN KEY (runtime_run_id, source_id) REFERENCES evidence_sources(runtime_run_id, source_id) ON DELETE CASCADE
                )
                """
            )
            now = _utc_now()
            conn.execute(
                """
                INSERT OR REPLACE INTO persistence_metadata(key, value, updated_at)
                VALUES (?, ?, ?)
                """,
                ("schema_version", self.schema_version, now),
            )
            conn.execute(
                """
                INSERT OR REPLACE INTO persistence_metadata(key, value, updated_at)
                VALUES (?, ?, ?)
                """,
                ("store_type", "sqlite", now),
            )

    def persist(self, runtime_run_id: str, ingestion: IngestionResult) -> EvidencePersistenceRecord:
        record = _build_record(
            runtime_run_id,
            ingestion,
            storage_mode="sqlite",
            path=self.database_path,
            schema_version=self.schema_version,
        )
        with self._connect() as conn:
            conn.execute("DELETE FROM runtime_runs WHERE runtime_run_id = ?", (runtime_run_id,))
            conn.execute(
                """
                INSERT INTO runtime_runs(
                    runtime_run_id,
                    subject_company,
                    storage_mode,
                    persisted_at,
                    schema_version,
                    source_count,
                    evidence_count,
                    validation_error_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.runtime_run_id,
                    record.subject_company,
                    record.storage_mode,
                    record.persisted_at,
                    record.schema_version,
                    record.source_count,
                    record.evidence_count,
                    len(ingestion.validation_errors),
                ),
            )
            conn.executemany(
                """
                INSERT INTO evidence_sources(
                    runtime_run_id,
                    source_id,
                    source_type,
                    title,
                    credibility_score,
                    url
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        runtime_run_id,
                        source.source_id,
                        source.source_type.value,
                        source.title,
                        source.credibility_score,
                        source.url,
                    )
                    for source in ingestion.sources
                ],
            )
            conn.executemany(
                """
                INSERT INTO evidence_items(
                    runtime_run_id,
                    evidence_id,
                    source_id,
                    lens,
                    claim,
                    relevance_score
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        runtime_run_id,
                        item.evidence_id,
                        item.source_id,
                        item.lens.value,
                        item.claim,
                        item.relevance_score,
                    )
                    for item in ingestion.evidence_items
                ],
            )
        return record

    def load_record(self, runtime_run_id: str) -> EvidencePersistenceRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT runtime_run_id, subject_company, storage_mode, persisted_at, schema_version, source_count, evidence_count
                FROM runtime_runs WHERE runtime_run_id = ?
                """,
                (runtime_run_id,),
            ).fetchone()
        if row is None:
            return None
        source_ids = self._fetch_column("evidence_sources", "source_id", runtime_run_id)
        evidence_ids = self._fetch_column("evidence_items", "evidence_id", runtime_run_id)
        return EvidencePersistenceRecord(
            runtime_run_id=str(row[0]),
            subject_company=str(row[1]),
            storage_mode=str(row[2]),
            persisted_at=str(row[3]),
            schema_version=str(row[4]),
            source_count=int(row[5]),
            evidence_count=int(row[6]),
            source_ids=source_ids,
            evidence_ids=evidence_ids,
            path=self.database_path,
        )

    def _fetch_column(self, table: str, column: str, runtime_run_id: str) -> list[str]:
        if table not in {"evidence_sources", "evidence_items"}:
            raise ValueError("unsupported_table")
        if column not in {"source_id", "evidence_id"}:
            raise ValueError("unsupported_column")
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT {column} FROM {table} WHERE runtime_run_id = ? ORDER BY {column}",
                (runtime_run_id,),
            ).fetchall()
        return [str(row[0]) for row in rows]

    def list_runtime_runs(self) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT runtime_run_id, subject_company, persisted_at, source_count, evidence_count, validation_error_count
                FROM runtime_runs ORDER BY persisted_at DESC
                """
            ).fetchall()
        return [
            {
                "runtime_run_id": str(row[0]),
                "subject_company": str(row[1]),
                "persisted_at": str(row[2]),
                "source_count": int(row[3]),
                "evidence_count": int(row[4]),
                "validation_error_count": int(row[5]),
            }
            for row in rows
        ]

    def count_rows(self, table: str) -> int:
        if table not in set(SQLITE_EVIDENCE_TABLES):
            raise ValueError("unsupported_table")
        with self._connect() as conn:
            row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
        return int(row[0])


def _build_record(
    runtime_run_id: str,
    ingestion: IngestionResult,
    storage_mode: str,
    path: str | None,
    schema_version: str = MODULE_8_EVIDENCE_SCHEMA_VERSION,
) -> EvidencePersistenceRecord:
    source_ids = [source.source_id for source in ingestion.sources]
    evidence_ids = [item.evidence_id for item in ingestion.evidence_items]
    return EvidencePersistenceRecord(
        runtime_run_id=runtime_run_id,
        subject_company=ingestion.subject_company,
        storage_mode=storage_mode,
        persisted_at=_utc_now(),
        source_ids=source_ids,
        evidence_ids=evidence_ids,
        path=path,
        schema_version=schema_version,
        source_count=len(source_ids),
        evidence_count=len(evidence_ids),
    )


def build_evidence_store(settings: EvidencePersistenceSettings) -> EvidenceStore:
    if settings.storage_mode in {"sqlite", "sqlite_durable", "durable_sqlite"}:
        return SQLiteEvidenceStore(settings.local_path, settings.schema_version)
    if settings.storage_mode == "filesystem":
        return FileSystemEvidenceStore(settings.local_path)
    return InMemoryEvidenceStore()


def summarize_evidence_schema(tables: Iterable[str] = SQLITE_EVIDENCE_TABLES) -> dict[str, object]:
    return {
        "schema_version": MODULE_8_EVIDENCE_SCHEMA_VERSION,
        "durable_store": "sqlite",
        "default_storage_mode": "in_memory",
        "supported_storage_modes": ["in_memory", "filesystem", "sqlite"],
        "tables": list(tables),
    }
