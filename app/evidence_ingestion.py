from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Union

from app.domain_contracts import (
    AnalyticalLens,
    EvidenceItemContract,
    EvidenceSourceContract,
    EvidenceSourceType,
    InsightDomainContract,
    REQUIRED_BRIEF_LENSES,
    build_default_domain_contract,
    validate_evidence_against_contract,
)

LensKey = Union[AnalyticalLens, str]
SourceTypeKey = Union[EvidenceSourceType, str]


def _coerce_source_type(value: SourceTypeKey) -> EvidenceSourceType:
    if isinstance(value, EvidenceSourceType):
        return value
    return EvidenceSourceType(str(value))


def _coerce_lens(value: LensKey) -> AnalyticalLens:
    if isinstance(value, AnalyticalLens):
        return value
    return AnalyticalLens(str(value))


@dataclass(frozen=True)
class RawEvidenceDocument:
    document_id: str
    source_id: str
    source_type: SourceTypeKey
    title: str
    content: str
    credibility_score: float
    claims_by_lens: Dict[LensKey, str]
    url: str | None = None

    def to_source_contract(self) -> EvidenceSourceContract:
        return EvidenceSourceContract(
            source_id=self.source_id,
            source_type=_coerce_source_type(self.source_type),
            title=self.title,
            credibility_score=self.credibility_score,
            url=self.url,
        )


@dataclass(frozen=True)
class IngestionResult:
    subject_company: str
    sources: List[EvidenceSourceContract]
    evidence_items: List[EvidenceItemContract]
    validation_errors: List[str]
    coverage_by_lens: Dict[str, int]

    @property
    def accepted(self) -> bool:
        return not self.validation_errors

    def to_dict(self) -> Dict[str, object]:
        return {
            "subject_company": self.subject_company,
            "accepted": self.accepted,
            "sources": [source.to_dict() for source in self.sources],
            "evidence_items": [item.to_dict() for item in self.evidence_items],
            "validation_errors": list(self.validation_errors),
            "coverage_by_lens": dict(self.coverage_by_lens),
        }


def ingest_documents(contract: InsightDomainContract, documents: Iterable[RawEvidenceDocument]) -> IngestionResult:
    source_by_id: Dict[str, EvidenceSourceContract] = {}
    evidence_items: List[EvidenceItemContract] = []

    for document in documents:
        source_by_id.setdefault(document.source_id, document.to_source_contract())
        for lens_key, claim in document.claims_by_lens.items():
            lens = _coerce_lens(lens_key)
            evidence_items.append(
                EvidenceItemContract(
                    evidence_id=f"{document.document_id}:{lens.value}",
                    source_id=document.source_id,
                    claim=claim,
                    lens=lens,
                    relevance_score=min(1.0, max(0.0, document.credibility_score)),
                )
            )

    sources = list(source_by_id.values())
    validation_errors = validate_evidence_against_contract(contract, sources, evidence_items)
    coverage_by_lens = {lens.value: 0 for lens in REQUIRED_BRIEF_LENSES}
    for item in evidence_items:
        coverage_by_lens[item.lens.value] = coverage_by_lens.get(item.lens.value, 0) + 1

    return IngestionResult(
        subject_company=contract.subject.company_name,
        sources=sources,
        evidence_items=evidence_items,
        validation_errors=validation_errors,
        coverage_by_lens=coverage_by_lens,
    )


def build_complete_sample_document(company_name: str) -> RawEvidenceDocument:
    claims = {
        lens: f"{company_name} evidence claim for {lens.value.replace('_', ' ')}."
        for lens in REQUIRED_BRIEF_LENSES
    }
    return RawEvidenceDocument(
        document_id="sample_complete_doc",
        source_id="sample_source",
        source_type=EvidenceSourceType.PUBLIC_WEB,
        title=f"Sample evidence packet for {company_name}",
        content=f"Deterministic evidence packet for {company_name}.",
        credibility_score=0.9,
        claims_by_lens=claims,
        url=None,
    )


def build_ingestion_summary(company_name: str) -> Dict[str, object]:
    contract = build_default_domain_contract(company_name)
    result = ingest_documents(contract, [build_complete_sample_document(company_name)])
    return result.to_dict()
