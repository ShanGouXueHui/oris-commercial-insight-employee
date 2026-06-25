from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable

MODULE_17_REUSE_ADOPTION_VERSION = "2026-06-25-module-17"


class ReuseCandidateType(str, Enum):
    GITHUB_SKILL = "github_skill"
    OPENCLAW_SKILL = "openclaw_skill"
    HARNESS = "harness"
    AGENTS_MD = "agents_md"


class ReuseDecision(str, Enum):
    ADOPT = "adopt"
    FORK_AND_ADAPT = "fork_and_adapt"
    DEFER = "defer"
    REJECT = "reject"


@dataclass(frozen=True)
class ReuseCandidate:
    name: str
    candidate_type: ReuseCandidateType
    source: str
    stars: int = 0
    downloads: int = 0
    maintenance_score: int = 0
    security_score: int = 0
    license_approved: bool = False
    fits_product_boundary: bool = False
    requires_network: bool = False
    requires_secret: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["candidate_type"] = self.candidate_type.value
        return payload


@dataclass(frozen=True)
class ReuseAssessment:
    candidate: ReuseCandidate
    score: int
    decision: ReuseDecision
    reasons: tuple[str, ...]
    adoption_boundary: str

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate": self.candidate.to_dict(),
            "score": self.score,
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "adoption_boundary": self.adoption_boundary,
        }


def calculate_reuse_score(candidate: ReuseCandidate) -> int:
    score = 0
    if candidate.stars >= 1000:
        score += 20
    elif candidate.stars >= 100:
        score += 10
    if candidate.downloads >= 10000:
        score += 20
    elif candidate.downloads >= 1000:
        score += 10
    score += min(max(candidate.maintenance_score, 0), 20)
    score += min(max(candidate.security_score, 0), 20)
    if candidate.license_approved:
        score += 10
    if candidate.fits_product_boundary:
        score += 10
    if candidate.requires_network:
        score -= 10
    if candidate.requires_secret:
        score -= 10
    return max(score, 0)


def assess_reuse_candidate(candidate: ReuseCandidate) -> ReuseAssessment:
    reasons: list[str] = []
    score = calculate_reuse_score(candidate)
    if not candidate.license_approved:
        reasons.append("license_not_approved")
    if not candidate.fits_product_boundary:
        reasons.append("product_boundary_mismatch")
    if candidate.requires_network:
        reasons.append("requires_network_boundary")
    if candidate.requires_secret:
        reasons.append("requires_secret_boundary")
    if candidate.maintenance_score < 10:
        reasons.append("maintenance_signal_low")
    if candidate.security_score < 10:
        reasons.append("security_signal_low")

    if not candidate.license_approved or candidate.security_score < 8:
        decision = ReuseDecision.REJECT
    elif score >= 75 and candidate.fits_product_boundary and not candidate.requires_secret:
        decision = ReuseDecision.ADOPT
    elif score >= 55 and candidate.fits_product_boundary:
        decision = ReuseDecision.FORK_AND_ADAPT
    else:
        decision = ReuseDecision.DEFER

    return ReuseAssessment(
        candidate=candidate,
        score=score,
        decision=decision,
        reasons=tuple(reasons),
        adoption_boundary="evaluate_before_custom_build",
    )


def assess_reuse_candidates(candidates: Iterable[ReuseCandidate]) -> list[ReuseAssessment]:
    return [assess_reuse_candidate(candidate) for candidate in candidates]


def default_reuse_candidates() -> tuple[ReuseCandidate, ...]:
    return (
        ReuseCandidate(
            name="github-pr-triage-skill",
            candidate_type=ReuseCandidateType.GITHUB_SKILL,
            source="github_connector_or_public_repo",
            stars=1000,
            downloads=10000,
            maintenance_score=18,
            security_score=18,
            license_approved=True,
            fits_product_boundary=True,
        ),
        ReuseCandidate(
            name="openclaw-execution-harness",
            candidate_type=ReuseCandidateType.HARNESS,
            source="openclaw_or_internal_harness_registry",
            stars=1000,
            downloads=10000,
            maintenance_score=16,
            security_score=16,
            license_approved=True,
            fits_product_boundary=True,
            requires_network=False,
            requires_secret=False,
        ),
        ReuseCandidate(
            name="agents-md-project-instructions-template",
            candidate_type=ReuseCandidateType.AGENTS_MD,
            source="industry_template_or_project_template",
            stars=100,
            downloads=1000,
            maintenance_score=15,
            security_score=15,
            license_approved=True,
            fits_product_boundary=True,
        ),
        ReuseCandidate(
            name="live-provider-sdk-skill",
            candidate_type=ReuseCandidateType.OPENCLAW_SKILL,
            source="openclaw_skill_registry",
            stars=1000,
            downloads=10000,
            maintenance_score=14,
            security_score=14,
            license_approved=True,
            fits_product_boundary=True,
            requires_network=True,
            requires_secret=True,
        ),
    )


def build_reuse_adoption_plan(candidates: Iterable[ReuseCandidate] | None = None) -> dict[str, object]:
    active_candidates = tuple(candidates or default_reuse_candidates())
    assessments = assess_reuse_candidates(active_candidates)
    return {
        "reuse_adoption_version": MODULE_17_REUSE_ADOPTION_VERSION,
        "principle": "reuse_high_quality_skills_before_custom_build",
        "candidate_count": len(active_candidates),
        "assessments": [assessment.to_dict() for assessment in assessments],
        "adopt": [item.candidate.name for item in assessments if item.decision == ReuseDecision.ADOPT],
        "fork_and_adapt": [item.candidate.name for item in assessments if item.decision == ReuseDecision.FORK_AND_ADAPT],
        "defer": [item.candidate.name for item in assessments if item.decision == ReuseDecision.DEFER],
        "reject": [item.candidate.name for item in assessments if item.decision == ReuseDecision.REJECT],
        "harness_upgrade_recommended": True,
        "agents_md_reuse_recommended": True,
        "custom_code_default": False,
    }


def summarize_reuse_adoption_boundary() -> dict[str, object]:
    plan = build_reuse_adoption_plan()
    return {
        "reuse_adoption_version": MODULE_17_REUSE_ADOPTION_VERSION,
        "candidate_count": plan["candidate_count"],
        "adopt_count": len(plan["adopt"]),
        "fork_and_adapt_count": len(plan["fork_and_adapt"]),
        "defer_count": len(plan["defer"]),
        "reject_count": len(plan["reject"]),
        "harness_upgrade_recommended": plan["harness_upgrade_recommended"],
        "agents_md_reuse_recommended": plan["agents_md_reuse_recommended"],
        "custom_code_default": plan["custom_code_default"],
    }
