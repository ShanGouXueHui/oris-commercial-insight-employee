from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, List

from app.brief_pipeline import GeneratedExecutiveBrief, build_sample_brief


class GateStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class QualityGateResult:
    gate_id: str
    status: GateStatus
    score: float
    threshold: float
    message: str

    def to_dict(self) -> Dict[str, object]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True)
class QualityAssessment:
    accepted: bool
    overall_status: GateStatus
    gate_results: List[QualityGateResult]
    limitations: List[str]
    recommended_action: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "accepted": self.accepted,
            "overall_status": self.overall_status.value,
            "gate_results": [item.to_dict() for item in self.gate_results],
            "limitations": list(self.limitations),
            "recommended_action": self.recommended_action,
        }


def _score_to_status(score: float, threshold: float, warn_margin: float = 0.1) -> GateStatus:
    if score >= threshold:
        return GateStatus.PASS
    if score >= max(0.0, threshold - warn_margin):
        return GateStatus.WARN
    return GateStatus.FAIL


def assess_brief_quality(brief: GeneratedExecutiveBrief) -> QualityAssessment:
    section_count = len(brief.sections)
    linked_sections = sum(1 for section in brief.sections if section.evidence_ids)
    evidence_linkage_score = linked_sections / section_count if section_count else 0.0
    confidence_score = brief.confidence_score
    risk_scenario_score = 1.0 if brief.risks and brief.scenarios else 0.0
    limitation_score = 1.0 if brief.accepted and not brief.limitations else 0.5 if brief.limitations else 0.8

    gates = [
        QualityGateResult(
            gate_id="minimum_confidence",
            status=_score_to_status(confidence_score, 0.65),
            score=confidence_score,
            threshold=0.65,
            message="Overall brief confidence must meet the minimum threshold.",
        ),
        QualityGateResult(
            gate_id="evidence_linkage",
            status=_score_to_status(evidence_linkage_score, 0.8),
            score=round(evidence_linkage_score, 2),
            threshold=0.8,
            message="Most generated sections must link back to evidence IDs.",
        ),
        QualityGateResult(
            gate_id="risk_and_scenario_presence",
            status=_score_to_status(risk_scenario_score, 1.0),
            score=risk_scenario_score,
            threshold=1.0,
            message="Brief must include at least one risk and scenario set.",
        ),
        QualityGateResult(
            gate_id="limitations_control",
            status=_score_to_status(limitation_score, 0.8),
            score=limitation_score,
            threshold=0.8,
            message="Limitations must be absent for accepted briefs or explicit for incomplete briefs.",
        ),
    ]

    statuses = [gate.status for gate in gates]
    if GateStatus.FAIL in statuses:
        overall = GateStatus.FAIL
    elif GateStatus.WARN in statuses:
        overall = GateStatus.WARN
    else:
        overall = GateStatus.PASS

    accepted = brief.accepted and overall != GateStatus.FAIL
    recommended_action = "publish" if accepted and overall == GateStatus.PASS else "review" if overall == GateStatus.WARN else "repair"
    limitations = list(brief.limitations)
    if not limitations and overall != GateStatus.PASS:
        limitations.append("Quality gates did not all pass; human or runtime repair review is required.")

    return QualityAssessment(
        accepted=accepted,
        overall_status=overall,
        gate_results=gates,
        limitations=limitations,
        recommended_action=recommended_action,
    )


def assess_sample_brief(company_name: str) -> Dict[str, object]:
    brief_dict = build_sample_brief(company_name)
    from app.brief_pipeline import GeneratedBriefSection, GeneratedRisk, GeneratedScenario, GeneratedExecutiveBrief
    from app.domain_contracts import AnalyticalLens

    sections = [
        GeneratedBriefSection(
            lens=AnalyticalLens(item["lens"]),
            title=item["title"],
            content=item["content"],
            evidence_ids=list(item["evidence_ids"]),
            confidence_score=float(item["confidence_score"]),
        )
        for item in brief_dict["sections"]
    ]
    risks = [GeneratedRisk(**item) for item in brief_dict["risks"]]
    scenarios = [GeneratedScenario(**item) for item in brief_dict["scenarios"]]
    brief = GeneratedExecutiveBrief(
        company_name=str(brief_dict["company_name"]),
        sections=sections,
        risks=risks,
        scenarios=scenarios,
        limitations=list(brief_dict["limitations"]),
        confidence_score=float(brief_dict["confidence_score"]),
        accepted=bool(brief_dict["accepted"]),
    )
    return assess_brief_quality(brief).to_dict()
