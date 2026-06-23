from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class InsightVertical(str, Enum):
    RETAIL = "retail"
    FINANCIAL_SERVICES = "financial_services"
    GOVERNMENT = "government"
    AUTOMOTIVE = "automotive"
    MANUFACTURING = "manufacturing"
    TECHNOLOGY = "technology"
    GENERAL = "general"


class EvidenceSourceType(str, Enum):
    PUBLIC_WEB = "public_web"
    COMPANY_DISCLOSURE = "company_disclosure"
    INTERNAL_NOTE = "internal_note"
    MARKET_DATA = "market_data"
    USER_PROVIDED = "user_provided"


class AnalyticalLens(str, Enum):
    COMPANY_PROFILE = "company_profile"
    MARKET_STRUCTURE = "market_structure"
    COMPETITOR_LANDSCAPE = "competitor_landscape"
    FINANCIAL_QUALITY = "financial_quality"
    PRODUCT_CAPABILITY = "product_capability"
    STRATEGY_SIGNALS = "strategy_signals"
    RISKS = "risks"
    SCENARIOS = "scenarios"
    LIMITATIONS = "limitations"


REQUIRED_BRIEF_LENSES = [
    AnalyticalLens.COMPANY_PROFILE,
    AnalyticalLens.MARKET_STRUCTURE,
    AnalyticalLens.COMPETITOR_LANDSCAPE,
    AnalyticalLens.FINANCIAL_QUALITY,
    AnalyticalLens.PRODUCT_CAPABILITY,
    AnalyticalLens.STRATEGY_SIGNALS,
    AnalyticalLens.RISKS,
    AnalyticalLens.SCENARIOS,
    AnalyticalLens.LIMITATIONS,
]


def _require_non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name}_required")


def _validate_probability(value: float, field_name: str) -> None:
    if value < 0.0 or value > 1.0:
        raise ValueError(f"{field_name}_must_be_0_to_1")


@dataclass(frozen=True)
class InsightSubject:
    company_name: str
    vertical: InsightVertical = InsightVertical.GENERAL
    geography: str = "global"
    time_horizon: str = "12_months"

    def __post_init__(self) -> None:
        _require_non_empty(self.company_name, "company_name")
        _require_non_empty(self.geography, "geography")
        _require_non_empty(self.time_horizon, "time_horizon")

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["vertical"] = self.vertical.value
        return data


@dataclass(frozen=True)
class EvidenceSourceContract:
    source_id: str
    source_type: EvidenceSourceType
    title: str
    credibility_score: float
    url: Optional[str] = None

    def __post_init__(self) -> None:
        _require_non_empty(self.source_id, "source_id")
        _require_non_empty(self.title, "title")
        _validate_probability(self.credibility_score, "credibility_score")

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["source_type"] = self.source_type.value
        return data


@dataclass(frozen=True)
class EvidenceItemContract:
    evidence_id: str
    source_id: str
    claim: str
    lens: AnalyticalLens
    relevance_score: float

    def __post_init__(self) -> None:
        _require_non_empty(self.evidence_id, "evidence_id")
        _require_non_empty(self.source_id, "source_id")
        _require_non_empty(self.claim, "claim")
        _validate_probability(self.relevance_score, "relevance_score")

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["lens"] = self.lens.value
        return data


@dataclass(frozen=True)
class BriefSectionContract:
    lens: AnalyticalLens
    title: str
    min_evidence_items: int = 1
    required: bool = True

    def __post_init__(self) -> None:
        _require_non_empty(self.title, "title")
        if self.min_evidence_items < 0:
            raise ValueError("min_evidence_items_must_be_non_negative")

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["lens"] = self.lens.value
        return data


@dataclass(frozen=True)
class InsightDomainContract:
    subject: InsightSubject
    required_sections: List[BriefSectionContract]
    accepted_source_types: List[EvidenceSourceType]
    quality_gates: Dict[str, float] = field(default_factory=lambda: {
        "minimum_overall_confidence": 0.65,
        "minimum_source_credibility": 0.5,
        "minimum_evidence_relevance": 0.5,
    })

    def __post_init__(self) -> None:
        lenses = [section.lens for section in self.required_sections]
        missing = [lens for lens in REQUIRED_BRIEF_LENSES if lens not in lenses]
        if missing:
            raise ValueError("missing_required_lenses:" + ",".join(lens.value for lens in missing))
        if not self.accepted_source_types:
            raise ValueError("accepted_source_types_required")
        for key, value in self.quality_gates.items():
            _validate_probability(value, key)

    def to_dict(self) -> Dict[str, object]:
        return {
            "subject": self.subject.to_dict(),
            "required_sections": [section.to_dict() for section in self.required_sections],
            "accepted_source_types": [item.value for item in self.accepted_source_types],
            "quality_gates": dict(self.quality_gates),
        }


def build_default_domain_contract(company_name: str, vertical: InsightVertical = InsightVertical.GENERAL) -> InsightDomainContract:
    subject = InsightSubject(company_name=company_name, vertical=vertical)
    sections = [
        BriefSectionContract(lens=lens, title=lens.value.replace("_", " ").title())
        for lens in REQUIRED_BRIEF_LENSES
    ]
    return InsightDomainContract(
        subject=subject,
        required_sections=sections,
        accepted_source_types=[
            EvidenceSourceType.PUBLIC_WEB,
            EvidenceSourceType.COMPANY_DISCLOSURE,
            EvidenceSourceType.MARKET_DATA,
            EvidenceSourceType.USER_PROVIDED,
        ],
    )


def validate_evidence_against_contract(
    contract: InsightDomainContract,
    sources: List[EvidenceSourceContract],
    evidence: List[EvidenceItemContract],
) -> List[str]:
    errors: List[str] = []
    source_by_id = {source.source_id: source for source in sources}
    accepted = set(contract.accepted_source_types)
    for source in sources:
        if source.source_type not in accepted:
            errors.append(f"source_type_not_accepted:{source.source_id}")
        if source.credibility_score < contract.quality_gates["minimum_source_credibility"]:
            errors.append(f"source_credibility_below_gate:{source.source_id}")
    for item in evidence:
        if item.source_id not in source_by_id:
            errors.append(f"missing_source:{item.evidence_id}")
        if item.relevance_score < contract.quality_gates["minimum_evidence_relevance"]:
            errors.append(f"evidence_relevance_below_gate:{item.evidence_id}")
    evidence_lenses = {item.lens for item in evidence}
    for section in contract.required_sections:
        if section.required and section.min_evidence_items > 0 and section.lens not in evidence_lenses:
            errors.append(f"missing_evidence_for_lens:{section.lens.value}")
    return errors
