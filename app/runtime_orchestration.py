from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Protocol

from app.brief_pipeline import GeneratedExecutiveBrief, generate_executive_brief_from_ingestion
from app.config import ProductSettings, load_product_settings
from app.domain_contracts import InsightVertical, build_default_domain_contract
from app.evidence_ingestion import IngestionResult, ingest_documents
from app.evidence_persistence import EvidencePersistenceRecord, EvidenceStore, build_evidence_store
from app.quality_gates import QualityAssessment, assess_brief_quality
from app.source_connectors import EvidenceSourceConnector, SourceConnectorResult, SourceQuery, build_source_connector


def _vertical_value(value: InsightVertical | str) -> str:
    return value.value if isinstance(value, InsightVertical) else str(value)


@dataclass(frozen=True)
class RuntimeV2RunRequest:
    company_name: str
    vertical: InsightVertical | str = InsightVertical.GENERAL
    geography: str = "global"
    time_horizon: str = "12_months"
    use_sample_evidence: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "company_name": self.company_name,
            "vertical": _vertical_value(self.vertical),
            "geography": self.geography,
            "time_horizon": self.time_horizon,
            "use_sample_evidence": self.use_sample_evidence,
        }


@dataclass(frozen=True)
class RuntimeV2RunResult:
    runtime_run_id: str
    runtime_adapter: str
    runtime_v2_reference: str
    request: RuntimeV2RunRequest
    source_result: SourceConnectorResult
    ingestion: IngestionResult
    brief: GeneratedExecutiveBrief
    quality: QualityAssessment
    persistence_record: EvidencePersistenceRecord
    settings_snapshot: dict[str, object]

    @property
    def accepted(self) -> bool:
        return self.quality.accepted

    def to_dict(self) -> dict[str, object]:
        return {
            "runtime_run_id": self.runtime_run_id,
            "runtime_adapter": self.runtime_adapter,
            "runtime_v2_reference": self.runtime_v2_reference,
            "runtime_v2_backed": True,
            "request": self.request.to_dict(),
            "source": self.source_result.to_dict(),
            "ingestion": self.ingestion.to_dict(),
            "brief": self.brief.to_dict(),
            "quality": self.quality.to_dict(),
            "evidence_persistence": self.persistence_record.to_dict(),
            "settings_snapshot": self.settings_snapshot,
        }


class RuntimeV2OrchestrationAdapter(Protocol):
    def execute(self, request: RuntimeV2RunRequest) -> RuntimeV2RunResult:
        """Execute one commercial insight run through the product-side Runtime v2 contract."""


class LocalRuntimeV2OrchestrationAdapter:
    """Product-side Runtime v2 adapter contract backed by deterministic local components."""

    def __init__(
        self,
        settings: ProductSettings | None = None,
        source_connector: EvidenceSourceConnector | None = None,
        evidence_store: EvidenceStore | None = None,
    ) -> None:
        self.settings = settings or load_product_settings()
        self.source_connector = source_connector or build_source_connector(self.settings.source)
        self.evidence_store = evidence_store or build_evidence_store(self.settings.evidence_persistence)

    def execute(self, request: RuntimeV2RunRequest) -> RuntimeV2RunResult:
        vertical = InsightVertical(_vertical_value(request.vertical))
        contract = build_default_domain_contract(request.company_name, vertical)
        source_query = SourceQuery(
            company_name=request.company_name,
            vertical=vertical,
            geography=request.geography,
            time_horizon=request.time_horizon,
        )
        source_result = self.source_connector.fetch(source_query)
        documents = source_result.documents if request.use_sample_evidence else []
        ingestion = ingest_documents(contract, documents)
        brief = generate_executive_brief_from_ingestion(ingestion)
        quality = assess_brief_quality(brief)
        runtime_run_id = build_runtime_run_id(request, self.settings.source.connector_mode)
        persistence_record = self.evidence_store.persist(runtime_run_id, ingestion)
        return RuntimeV2RunResult(
            runtime_run_id=runtime_run_id,
            runtime_adapter=self.settings.runtime.adapter_mode,
            runtime_v2_reference=self.settings.runtime.runtime_v2_reference,
            request=request,
            source_result=source_result,
            ingestion=ingestion,
            brief=brief,
            quality=quality,
            persistence_record=persistence_record,
            settings_snapshot=self.settings.to_dict(),
        )


def build_runtime_run_id(request: RuntimeV2RunRequest, source_mode: str) -> str:
    raw = "|".join(
        [
            request.company_name.strip().lower(),
            _vertical_value(request.vertical),
            request.geography,
            request.time_horizon,
            source_mode,
            str(request.use_sample_evidence),
        ]
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"rtv2-{digest}"


def run_local_runtime_v2_insight(
    company_name: str,
    vertical: InsightVertical | str = InsightVertical.GENERAL,
    use_sample_evidence: bool = True,
) -> RuntimeV2RunResult:
    adapter = LocalRuntimeV2OrchestrationAdapter()
    return adapter.execute(
        RuntimeV2RunRequest(
            company_name=company_name,
            vertical=vertical,
            use_sample_evidence=use_sample_evidence,
        )
    )
