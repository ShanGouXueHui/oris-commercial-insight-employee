from __future__ import annotations

from typing import Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.brief_pipeline import generate_executive_brief_from_ingestion
from app.domain_contracts import InsightVertical, build_default_domain_contract
from app.evidence_ingestion import build_complete_sample_document, ingest_documents
from app.quality_gates import assess_brief_quality

router = APIRouter(prefix="/insights/rebuild")


class RebuildBriefRequest(BaseModel):
    company_name: str = Field(min_length=1)
    vertical: InsightVertical = InsightVertical.GENERAL
    use_sample_evidence: bool = True


@router.get("/acceptance")
def rebuild_acceptance() -> Dict[str, object]:
    return {
        "status": "ready",
        "runtime_v2_backed": True,
        "next_step": "module_7_runtime_orchestration",
    }


@router.post("/brief")
def generate_rebuild_brief(request: RebuildBriefRequest) -> Dict[str, object]:
    contract = build_default_domain_contract(request.company_name, request.vertical)
    documents = [build_complete_sample_document(request.company_name)] if request.use_sample_evidence else []
    ingestion = ingest_documents(contract, documents)
    brief = generate_executive_brief_from_ingestion(ingestion)
    quality = assess_brief_quality(brief)
    return {
        "company_name": request.company_name,
        "runtime_v2_backed": True,
        "accepted": quality.accepted,
        "recommended_action": quality.recommended_action,
        "confidence_score": brief.confidence_score,
        "brief": brief.to_dict(),
        "quality": quality.to_dict(),
    }
