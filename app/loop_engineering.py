from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable

MODULE_18_LOOP_ENGINEERING_VERSION = "2026-06-25-module-18"


class LoopComponent(str, Enum):
    AUTOMATION = "automation"
    WORKTREE = "worktree"
    SKILL = "skill"
    CONNECTOR = "connector"
    SUB_AGENT = "sub_agent"
    EVIDENCE_GATE = "evidence_gate"
    BUDGET_GATE = "budget_gate"


class LoopDecision(str, Enum):
    ENABLE_BOUNDARY = "enable_boundary"
    DEFER = "defer"
    REJECT = "reject"


@dataclass(frozen=True)
class LoopDefinition:
    name: str
    goal: str
    components: tuple[LoopComponent, ...]
    max_iterations: int = 3
    max_token_budget: int = 100000
    requires_network: bool = False
    requires_secret: bool = False
    requires_human_acceptance: bool = True
    evidence_required: bool = True

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["components"] = [component.value for component in self.components]
        return payload


@dataclass(frozen=True)
class LoopAssessment:
    loop: LoopDefinition
    decision: LoopDecision
    reasons: tuple[str, ...]
    bounded: bool
    estimated_risk: str

    def to_dict(self) -> dict[str, object]:
        return {
            "loop": self.loop.to_dict(),
            "decision": self.decision.value,
            "reasons": list(self.reasons),
            "bounded": self.bounded,
            "estimated_risk": self.estimated_risk,
        }


def is_loop_bounded(loop: LoopDefinition) -> bool:
    return loop.max_iterations > 0 and loop.max_iterations <= 10 and loop.max_token_budget > 0 and loop.max_token_budget <= 500000


def assess_loop(loop: LoopDefinition) -> LoopAssessment:
    reasons: list[str] = []
    bounded = is_loop_bounded(loop)
    if not bounded:
        reasons.append("loop_not_bounded")
    if not loop.evidence_required:
        reasons.append("evidence_gate_missing")
    if loop.requires_network:
        reasons.append("requires_network_boundary")
    if loop.requires_secret:
        reasons.append("requires_secret_boundary")
    if LoopComponent.BUDGET_GATE not in loop.components:
        reasons.append("budget_gate_missing")
    if LoopComponent.EVIDENCE_GATE not in loop.components:
        reasons.append("evidence_gate_component_missing")

    if not bounded or not loop.evidence_required:
        decision = LoopDecision.REJECT
    elif loop.requires_secret or loop.requires_network:
        decision = LoopDecision.DEFER
    else:
        decision = LoopDecision.ENABLE_BOUNDARY

    if decision == LoopDecision.ENABLE_BOUNDARY:
        risk = "low"
    elif decision == LoopDecision.DEFER:
        risk = "medium"
    else:
        risk = "high"

    return LoopAssessment(loop=loop, decision=decision, reasons=tuple(reasons), bounded=bounded, estimated_risk=risk)


def default_loop_definitions() -> tuple[LoopDefinition, ...]:
    return (
        LoopDefinition(
            name="oris_page_improvement_loop",
            goal="Improve ORIS insight product pages through bounded reusable-skill review and evidence-backed edits.",
            components=(
                LoopComponent.AUTOMATION,
                LoopComponent.SKILL,
                LoopComponent.CONNECTOR,
                LoopComponent.EVIDENCE_GATE,
                LoopComponent.BUDGET_GATE,
            ),
            max_iterations=3,
            max_token_budget=80000,
        ),
        LoopDefinition(
            name="harness_upgrade_loop",
            goal="Evaluate OpenClaw or harness upgrade candidates before building custom execution scaffolding.",
            components=(
                LoopComponent.AUTOMATION,
                LoopComponent.WORKTREE,
                LoopComponent.SKILL,
                LoopComponent.EVIDENCE_GATE,
                LoopComponent.BUDGET_GATE,
            ),
            max_iterations=4,
            max_token_budget=120000,
        ),
        LoopDefinition(
            name="sub_agent_review_loop",
            goal="Split implementation and review into separate bounded agent roles.",
            components=(
                LoopComponent.AUTOMATION,
                LoopComponent.SUB_AGENT,
                LoopComponent.EVIDENCE_GATE,
                LoopComponent.BUDGET_GATE,
            ),
            max_iterations=2,
            max_token_budget=60000,
        ),
        LoopDefinition(
            name="live_provider_loop",
            goal="Evaluate live provider or remote runtime tasks only after explicit boundary approval.",
            components=(
                LoopComponent.AUTOMATION,
                LoopComponent.CONNECTOR,
                LoopComponent.SUB_AGENT,
                LoopComponent.EVIDENCE_GATE,
                LoopComponent.BUDGET_GATE,
            ),
            max_iterations=3,
            max_token_budget=100000,
            requires_network=True,
            requires_secret=True,
        ),
    )


def build_loop_engineering_plan(loops: Iterable[LoopDefinition] | None = None) -> dict[str, object]:
    active_loops = tuple(loops or default_loop_definitions())
    assessments = [assess_loop(loop) for loop in active_loops]
    return {
        "loop_engineering_version": MODULE_18_LOOP_ENGINEERING_VERSION,
        "principle": "design_bounded_loops_that_prompt_agents",
        "loop_count": len(active_loops),
        "assessments": [assessment.to_dict() for assessment in assessments],
        "enabled_boundaries": [item.loop.name for item in assessments if item.decision == LoopDecision.ENABLE_BOUNDARY],
        "deferred": [item.loop.name for item in assessments if item.decision == LoopDecision.DEFER],
        "rejected": [item.loop.name for item in assessments if item.decision == LoopDecision.REJECT],
        "budget_gate_required": True,
        "evidence_gate_required": True,
        "human_acceptance_required": True,
        "infinite_loop_allowed": False,
    }


def summarize_loop_engineering_boundary() -> dict[str, object]:
    plan = build_loop_engineering_plan()
    return {
        "loop_engineering_version": MODULE_18_LOOP_ENGINEERING_VERSION,
        "loop_count": plan["loop_count"],
        "enabled_boundary_count": len(plan["enabled_boundaries"]),
        "deferred_count": len(plan["deferred"]),
        "rejected_count": len(plan["rejected"]),
        "budget_gate_required": plan["budget_gate_required"],
        "evidence_gate_required": plan["evidence_gate_required"],
        "human_acceptance_required": plan["human_acceptance_required"],
        "infinite_loop_allowed": plan["infinite_loop_allowed"],
    }
