from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List

from app.domain_contracts import AnalyticalLens, REQUIRED_BRIEF_LENSES, build_default_domain_contract
from app.evidence_ingestion import IngestionResult, build_complete_sample_document, ingest_documents


@dataclass(frozen=True)
class GeneratedBriefSection:
    lens: AnalyticalLens
    title: str
    content: str
    evidence_ids: List[str]
    confidence_score: float

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["lens"] = self.lens.value
        return data


@dataclass(frozen=True)
class GeneratedRisk:
    category: str
    description: str
    probability: float
    impact: float
    evidence_ids: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GeneratedScenario:
    name: str
    description: str
    probability: float
    impact: float
    evidence_ids: List[str]

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class GeneratedExecutiveBrief:
    company_name: str
    sections: List[GeneratedBriefSection]
    risks: List[GeneratedRisk]
    scenarios: List[GeneratedScenario]
    limitations: List[str]
    confidence_score: float
    accepted: bool

    def to_dict(self) -> Dict[str, object]:
        return {
            "company_name": self.company_name,
            "sections": [section.to_dict() for section in self.sections],
            "risks": [risk.to_dict() for risk in self.risks],
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "limitations": list(self.limitations),
            "confidence_score": self.confidence_score,
            "accepted": self.accepted,
        }


def _items_by_lens(ingestion: IngestionResult) -> Dict[AnalyticalLens, List[str]]:
    grouped: Dict[AnalyticalLens, List[str]] = {lens: [] for lens in REQUIRED_BRIEF_LENSES}
    for item in ingestion.evidence_items:
        grouped.setdefault(item.lens, []).append(item.evidence_id)
    return grouped


def generate_sections(ingestion: IngestionResult) -> List[GeneratedBriefSection]:
    grouped = _items_by_lens(ingestion)
    sections: List[GeneratedBriefSection] = []
    for lens in REQUIRED_BRIEF_LENSES:
        evidence_ids = grouped.get(lens, [])
        readable = lens.value.replace("_", " ").title()
        coverage = len(evidence_ids)
        confidence = 0.8 if coverage else 0.35
        content = (
            f"{readable} for {ingestion.subject_company}: generated from {coverage} evidence item(s). "
            f"This section is deterministic and evidence-linked."
        )
        sections.append(
            GeneratedBriefSection(
                lens=lens,
                title=readable,
                content=content,
                evidence_ids=evidence_ids,
                confidence_score=confidence,
            )
        )
    return sections


def generate_risks(ingestion: IngestionResult) -> List[GeneratedRisk]:
    grouped = _items_by_lens(ingestion)
    ids = grouped.get(AnalyticalLens.RISKS, [])
    return [
        GeneratedRisk(
            category="evidence_quality",
            description="Insight quality depends on source credibility, lens coverage, and evidence recency.",
            probability=0.45,
            impact=0.7,
            evidence_ids=ids,
        )
    ]


def generate_scenarios(ingestion: IngestionResult) -> List[GeneratedScenario]:
    grouped = _items_by_lens(ingestion)
    ids = grouped.get(AnalyticalLens.SCENARIOS, [])
    return [
        GeneratedScenario(
            name="Base Case",
            description="Company trajectory follows currently observed evidence signals.",
            probability=0.5,
            impact=0.6,
            evidence_ids=ids,
        ),
        GeneratedScenario(
            name="Upside Case",
            description="Execution improves and evidence signals strengthen across core lenses.",
            probability=0.3,
            impact=0.8,
            evidence_ids=ids,
        ),
        GeneratedScenario(
            name="Downside Case",
            description="Risk signals dominate and evidence coverage weakens.",
            probability=0.2,
            impact=0.7,
            evidence_ids=ids,
        ),
    ]


def generate_executive_brief_from_ingestion(ingestion: IngestionResult) -> GeneratedExecutiveBrief:
    sections = generate_sections(ingestion)
    section_confidence = sum(section.confidence_score for section in sections) / len(sections)
    confidence = round(min(section_confidence, 0.85), 2) if ingestion.accepted else round(min(section_confidence, 0.55), 2)
    limitations = [] if ingestion.accepted else ["Ingestion validation errors exist; brief should be treated as incomplete."]
    limitations.extend(ingestion.validation_errors)
    return GeneratedExecutiveBrief(
        company_name=ingestion.subject_company,
        sections=sections,
        risks=generate_risks(ingestion),
        scenarios=generate_scenarios(ingestion),
        limitations=limitations,
        confidence_score=confidence,
        accepted=ingestion.accepted,
    )


def build_sample_brief(company_name: str) -> Dict[str, object]:
    contract = build_default_domain_contract(company_name)
    ingestion = ingest_documents(contract, [build_complete_sample_document(company_name)])
    return generate_executive_brief_from_ingestion(ingestion).to_dict()
