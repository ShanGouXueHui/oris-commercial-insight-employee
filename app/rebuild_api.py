from __future__ import annotations

from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import load_product_settings
from app.domain_contracts import InsightVertical
from app.evidence_persistence import summarize_evidence_schema
from app.observability import build_runtime_observability_snapshot
from app.runtime_orchestration import LocalRuntimeV2OrchestrationAdapter, RuntimeV2RunRequest
from app.source_connectors import summarize_connector_modes

router = APIRouter(prefix="/insights/rebuild")


class RebuildBriefRequest(BaseModel):
    company_name: str = Field(min_length=1)
    vertical: InsightVertical = InsightVertical.GENERAL
    use_sample_evidence: bool = True


@router.get("/acceptance")
def rebuild_acceptance() -> Dict[str, object]:
    settings = load_product_settings()
    observation = build_runtime_observability_snapshot(settings)
    return {
        "status": "ready",
        "runtime_v2_backed": True,
        "module_7_runtime_orchestration": True,
        "module_8_durable_persistence": True,
        "module_9_deployment_smoke_ready": True,
        "source_connector_boundary": True,
        "config_separated_settings": True,
        "evidence_persistence_boundary": True,
        "durable_evidence_store": "sqlite_available",
        "observability_boundary": True,
        "external_provider_boundary": "configured_but_disabled",
        "next_step": "run_module_9_smoke_then_module_10_provider_or_commercial_guardrails",
        "runtime": settings.runtime.to_dict(),
        "source": settings.source.to_dict(),
        "model": settings.model.to_dict(),
        "evidence_persistence": settings.evidence_persistence.to_dict(),
        "connector_modes": summarize_connector_modes(),
        "evidence_schema": summarize_evidence_schema(),
        "observability": observation.to_dict(),
    }


@router.post("/brief")
def generate_rebuild_brief(request: RebuildBriefRequest) -> Dict[str, object]:
    adapter = LocalRuntimeV2OrchestrationAdapter()
    run = adapter.execute(
        RuntimeV2RunRequest(
            company_name=request.company_name,
            vertical=request.vertical,
            use_sample_evidence=request.use_sample_evidence,
        )
    )
    run_payload = run.to_dict()
    return {
        "company_name": request.company_name,
        "runtime_v2_backed": True,
        "accepted": run.quality.accepted,
        "recommended_action": run.quality.recommended_action,
        "confidence_score": run.brief.confidence_score,
        "runtime_run_id": run.runtime_run_id,
        "runtime_adapter": run.runtime_adapter,
        "source_connector": run.source_result.metadata.to_dict(),
        "evidence_persistence": run.persistence_record.to_dict(),
        "brief": run.brief.to_dict(),
        "quality": run.quality.to_dict(),
        "runtime": run_payload,
    }
