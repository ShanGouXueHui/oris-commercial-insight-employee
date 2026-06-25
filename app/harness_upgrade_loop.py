from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable

from app.loop_engineering import LoopDecision, LoopDefinition, assess_loop, default_loop_definitions
from app.reuse_adoption import ReuseAssessment, ReuseCandidate, ReuseCandidateType, assess_reuse_candidate, default_reuse_candidates

MODULE_19_HARNESS_UPGRADE_LOOP_VERSION = "2026-06-25-module-19"


class HarnessUpgradeStepType(str, Enum):
    DISCOVER = "discover"
    ASSESS_REUSE = "assess_reuse"
    PLAN_WORKTREE = "plan_worktree"
    PLAN_TESTS = "plan_tests"
    WRITE_EVIDENCE = "write_evidence"
    REQUIRE_ACCEPTANCE = "require_acceptance"


@dataclass(frozen=True)
class HarnessUpgradeCandidate:
    name: str
    source: str
    target_component: str
    candidate: ReuseCandidate

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "source": self.source,
            "target_component": self.target_component,
            "candidate": self.candidate.to_dict(),
        }


@dataclass(frozen=True)
class HarnessUpgradeStep:
    step_type: HarnessUpgradeStepType
    description: str
    evidence_required: bool = True
    live_action: bool = False

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["step_type"] = self.step_type.value
        return payload


@dataclass(frozen=True)
class HarnessUpgradePlan:
    plan_version: str
    loop_name: str
    candidate: HarnessUpgradeCandidate
    reuse_assessment: ReuseAssessment
    loop_decision: LoopDecision
    steps: tuple[HarnessUpgradeStep, ...]
    package_installation_enabled: bool = False
    remote_code_fetch_enabled: bool = False
    production_harness_modified: bool = False
    human_acceptance_required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_version": self.plan_version,
            "loop_name": self.loop_name,
            "candidate": self.candidate.to_dict(),
            "reuse_assessment": self.reuse_assessment.to_dict(),
            "loop_decision": self.loop_decision.value,
            "steps": [step.to_dict() for step in self.steps],
            "package_installation_enabled": self.package_installation_enabled,
            "remote_code_fetch_enabled": self.remote_code_fetch_enabled,
            "production_harness_modified": self.production_harness_modified,
            "human_acceptance_required": self.human_acceptance_required,
        }


def _default_harness_loop() -> LoopDefinition:
    for loop in default_loop_definitions():
        if loop.name == "harness_upgrade_loop":
            return loop
    raise RuntimeError("harness_upgrade_loop_not_found")


def default_harness_upgrade_candidates() -> tuple[HarnessUpgradeCandidate, ...]:
    reusable = {candidate.name: candidate for candidate in default_reuse_candidates()}
    return (
        HarnessUpgradeCandidate(
            name="openclaw-execution-harness-upgrade",
            source="module_17_default_reuse_candidates",
            target_component="execution_harness",
            candidate=reusable["openclaw-execution-harness"],
        ),
        HarnessUpgradeCandidate(
            name="agents-md-operating-rules-upgrade",
            source="module_17_default_reuse_candidates",
            target_component="project_instructions",
            candidate=reusable["agents-md-project-instructions-template"],
        ),
    )


def build_harness_upgrade_steps() -> tuple[HarnessUpgradeStep, ...]:
    return (
        HarnessUpgradeStep(HarnessUpgradeStepType.DISCOVER, "Discover reusable harness or instruction template candidates."),
        HarnessUpgradeStep(HarnessUpgradeStepType.ASSESS_REUSE, "Assess candidate license, maintenance, security, and product boundary fit."),
        HarnessUpgradeStep(HarnessUpgradeStepType.PLAN_WORKTREE, "Plan an isolated worktree or branch for any future change; do not modify production harness in Module 19."),
        HarnessUpgradeStep(HarnessUpgradeStepType.PLAN_TESTS, "Define deterministic tests required before adoption."),
        HarnessUpgradeStep(HarnessUpgradeStepType.WRITE_EVIDENCE, "Write machine-readable evidence for candidate decision and loop outcome."),
        HarnessUpgradeStep(HarnessUpgradeStepType.REQUIRE_ACCEPTANCE, "Require user-controlled bootstrap evidence before acceptance."),
    )


def build_harness_upgrade_plan(candidate: HarnessUpgradeCandidate, loop: LoopDefinition | None = None) -> HarnessUpgradePlan:
    active_loop = loop or _default_harness_loop()
    loop_assessment = assess_loop(active_loop)
    reuse_assessment = assess_reuse_candidate(candidate.candidate)
    return HarnessUpgradePlan(
        plan_version=MODULE_19_HARNESS_UPGRADE_LOOP_VERSION,
        loop_name=active_loop.name,
        candidate=candidate,
        reuse_assessment=reuse_assessment,
        loop_decision=loop_assessment.decision,
        steps=build_harness_upgrade_steps(),
        package_installation_enabled=False,
        remote_code_fetch_enabled=False,
        production_harness_modified=False,
        human_acceptance_required=True,
    )


def build_harness_upgrade_plans(candidates: Iterable[HarnessUpgradeCandidate] | None = None) -> list[HarnessUpgradePlan]:
    active_candidates = tuple(candidates or default_harness_upgrade_candidates())
    return [build_harness_upgrade_plan(candidate) for candidate in active_candidates]


def summarize_harness_upgrade_loop() -> dict[str, object]:
    plans = build_harness_upgrade_plans()
    return {
        "harness_upgrade_loop_version": MODULE_19_HARNESS_UPGRADE_LOOP_VERSION,
        "plan_count": len(plans),
        "candidate_names": [plan.candidate.name for plan in plans],
        "adopt_or_adapt_count": sum(1 for plan in plans if plan.reuse_assessment.decision.value in {"adopt", "fork_and_adapt"}),
        "package_installation_enabled": False,
        "remote_code_fetch_enabled": False,
        "production_harness_modified": False,
        "human_acceptance_required": True,
        "evidence_required": True,
    }
