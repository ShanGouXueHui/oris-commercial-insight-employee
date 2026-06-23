from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


RUNTIME_V2_REQUIRED_CAPABILITIES = [
    "state_machine",
    "persistent_run_store",
    "worker_loop",
    "safe_executor_adapter",
    "github_evidence_publisher",
    "approval_gate",
    "acceptance_harness",
]

INSIGHT_REBUILD_MODULES = [
    "module_1_architecture_alignment",
    "module_2_domain_contracts",
    "module_3_evidence_ingestion",
    "module_4_brief_generation_pipeline",
    "module_5_quality_gates_and_limitations",
    "module_6_api_surface_and_acceptance",
]


@dataclass(frozen=True)
class RuntimeV2Alignment:
    product: str
    runtime_status: str
    architecture_mode: str
    required_capabilities: List[str]
    rebuild_modules: List[str]
    product_repo_mutation_allowed: bool

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def build_runtime_v2_alignment() -> RuntimeV2Alignment:
    return RuntimeV2Alignment(
        product="ORIS Commercial Insight Employee",
        runtime_status="accepted",
        architecture_mode="runtime_v2_backed_rebuild",
        required_capabilities=list(RUNTIME_V2_REQUIRED_CAPABILITIES),
        rebuild_modules=list(INSIGHT_REBUILD_MODULES),
        product_repo_mutation_allowed=True,
    )


def validate_alignment(alignment: RuntimeV2Alignment) -> List[str]:
    errors: List[str] = []
    if alignment.runtime_status != "accepted":
        errors.append("runtime_v2_not_accepted")
    if alignment.architecture_mode != "runtime_v2_backed_rebuild":
        errors.append("wrong_architecture_mode")
    missing = [item for item in RUNTIME_V2_REQUIRED_CAPABILITIES if item not in alignment.required_capabilities]
    if missing:
        errors.append("missing_capabilities:" + ",".join(missing))
    if not alignment.rebuild_modules or alignment.rebuild_modules[0] != "module_1_architecture_alignment":
        errors.append("invalid_rebuild_module_sequence")
    return errors


def build_architecture_summary() -> Dict[str, object]:
    alignment = build_runtime_v2_alignment()
    errors = validate_alignment(alignment)
    return {
        "alignment": alignment.to_dict(),
        "valid": not errors,
        "errors": errors,
        "next_module": "module_2_domain_contracts",
    }
