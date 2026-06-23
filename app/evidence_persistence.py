from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from app.config import EvidencePersistenceSettings
from app.evidence_ingestion import IngestionResult


@dataclass(frozen=True)
class EvidencePersistenceRecord:
    runtime_run_id: str
    subject_company: str
    storage_mode: str
    persisted_at: str
    source_ids: list[str]
    evidence_ids: list[str]
    path: str | None = None

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


def _build_record(
    runtime_run_id: str,
    ingestion: IngestionResult,
    storage_mode: str,
    path: str | None,
) -> EvidencePersistenceRecord:
    return EvidencePersistenceRecord(
        runtime_run_id=runtime_run_id,
        subject_company=ingestion.subject_company,
        storage_mode=storage_mode,
        persisted_at=datetime.now(timezone.utc).isoformat(),
        source_ids=[source.source_id for source in ingestion.sources],
        evidence_ids=[item.evidence_id for item in ingestion.evidence_items],
        path=path,
    )


def build_evidence_store(settings: EvidencePersistenceSettings) -> EvidenceStore:
    if settings.storage_mode == "filesystem":
        return FileSystemEvidenceStore(settings.local_path)
    return InMemoryEvidenceStore()
