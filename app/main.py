from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.commercial_guardrails import build_guardrail_ledger, evaluate_guardrails
from app.config import PRODUCT_API_VERSION, load_product_settings
from app.observability import build_runtime_observability_snapshot
from app.rebuild_api import router as rebuild_router
from app.tenant_guardrails import (
    build_local_tenant_entitlements,
    evaluate_tenant_entitlement_guardrails,
    summarize_tenant_middleware_usage_ledger_bridge,
    tenant_guardrail_policy_from_settings,
)


app = FastAPI(
    title="ORIS Commercial Insight Employee API",
    description="Standalone commercial insight employee product API",
    version=PRODUCT_API_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def commercial_guardrail_middleware(request: Request, call_next):
    settings = load_product_settings()
    ledger = build_guardrail_ledger()
    if settings.tenant_guardrails.enabled:
        tenant_decision = evaluate_tenant_entitlement_guardrails(
            path=request.url.path,
            method=request.method,
            headers=request.headers,
            settings=settings.commercial_guardrails,
            entitlements=build_local_tenant_entitlements(settings.tenant_guardrails),
            policy=tenant_guardrail_policy_from_settings(settings.tenant_guardrails),
            ledger=ledger,
        )
        commercial_decision = tenant_decision.commercial_guardrail
        if not tenant_decision.allowed:
            response = JSONResponse(
                status_code=tenant_decision.status_code,
                content={"tenant_guardrail": tenant_decision.to_dict()},
            )
        else:
            response = await call_next(request)
        response.headers["X-ORIS-Guardrail-Policy"] = str(commercial_decision.get("policy_version", ""))
        response.headers["X-ORIS-Guardrail-Mode"] = str(commercial_decision.get("enforcement_mode", ""))
        response.headers["X-ORIS-Guardrail-Reason"] = str(commercial_decision.get("reason", ""))
        response.headers["X-ORIS-Tenant-Guardrail-Version"] = tenant_decision.tenant_guardrail_version
        response.headers["X-ORIS-Tenant-Guardrail-Reason"] = tenant_decision.reason
        response.headers["X-ORIS-Tenant-ID"] = tenant_decision.tenant_id
        if tenant_decision.tenant_usage_ledger_enabled:
            response.headers["X-ORIS-Tenant-Usage-Ledger-Version"] = str(
                tenant_decision.tenant_usage_ledger_version or ""
            )
            response.headers["X-ORIS-Tenant-Usage-Consumed"] = str(tenant_decision.tenant_usage_consumed).lower()
            if tenant_decision.tenant_usage_request_count is not None:
                response.headers["X-ORIS-Tenant-Usage-Request-Count"] = str(
                    tenant_decision.tenant_usage_request_count
                )
        remaining_minute = commercial_decision.get("remaining_minute")
        remaining_day = commercial_decision.get("remaining_day")
        retry_after = commercial_decision.get("retry_after_seconds")
        if remaining_minute is not None:
            response.headers["X-ORIS-RateLimit-Remaining-Minute"] = str(remaining_minute)
        if remaining_day is not None:
            response.headers["X-ORIS-Quota-Remaining-Day"] = str(remaining_day)
        if retry_after is not None:
            response.headers["Retry-After"] = str(retry_after)
        return response

    decision = evaluate_guardrails(
        path=request.url.path,
        method=request.method,
        headers=request.headers,
        settings=settings.commercial_guardrails,
        ledger=ledger,
    )
    if not decision.allowed:
        payload = {
            "error": decision.error.to_dict() if decision.error else None,
            "guardrail": decision.to_dict(),
        }
        response = JSONResponse(status_code=decision.status_code, content=payload)
    else:
        response = await call_next(request)
    response.headers["X-ORIS-Guardrail-Policy"] = decision.policy_version
    response.headers["X-ORIS-Guardrail-Mode"] = decision.enforcement_mode
    response.headers["X-ORIS-Guardrail-Reason"] = decision.reason
    if decision.remaining_minute is not None:
        response.headers["X-ORIS-RateLimit-Remaining-Minute"] = str(decision.remaining_minute)
    if decision.remaining_day is not None:
        response.headers["X-ORIS-Quota-Remaining-Day"] = str(decision.remaining_day)
    if decision.retry_after_seconds is not None:
        response.headers["Retry-After"] = str(decision.retry_after_seconds)
    return response


app.include_router(rebuild_router)


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    content: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class RiskItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category: str
    description: str
    probability: float = Field(ge=0.0, le=1.0)
    impact: float = Field(ge=0.0, le=1.0)
    mitigation_strategy: Optional[str] = None
    evidence_refs: Optional[List[str]] = None


class ScenarioItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    probability: float = Field(ge=0.0, le=1.0)
    impact_on_business: float = Field(ge=0.0, le=1.0)
    key_drivers: Optional[List[str]] = None
    outcomes: Optional[List[str]] = None


class BriefSection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    evidence_refs: Optional[List[str]] = None
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.8)


class InsightRequest(BaseModel):
    company_name: str
    industry: Optional[str] = None
    focus_areas: Optional[List[str]] = None
    time_horizon: Optional[str] = None
    user_id: Optional[str] = None
    evidence_sources: Optional[List[str]] = None


class ExecutiveBriefResponse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str
    generated_at: datetime = Field(default_factory=datetime.now)
    company_profile: BriefSection
    market_structure: BriefSection
    competitor_landscape: BriefSection
    financial_quality: BriefSection
    product_capability: BriefSection
    strategy_signals: BriefSection
    risks: List[RiskItem]
    scenarios: List[ScenarioItem]
    evidence_references: List[EvidenceItem]
    limitations: BriefSection
    confidence_score: float = Field(ge=0.0, le=1.0)
    processing_time_ms: Optional[int] = None


@app.get("/healthz")
async def health_check() -> Dict[str, object]:
    return {"status": "healthy", "timestamp": datetime.now()}


@app.get("/healthz/details")
async def health_details() -> Dict[str, object]:
    settings = load_product_settings()
    observation = build_runtime_observability_snapshot(settings)
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": settings.api.version,
        "service": settings.api.service_name,
        "runtime_v2_backed_rebuild": True,
        "module_9_observability": True,
        "module_10_commercial_guardrails": True,
        "module_11_persistent_quota_ledger": True,
        "module_23_tenant_guardrail_middleware": True,
        "module_25_tenant_middleware_usage_ledger_bridge": True,
        "tenant_guardrails": settings.tenant_guardrails.to_dict(),
        "tenant_middleware_usage_ledger": summarize_tenant_middleware_usage_ledger_bridge(settings.tenant_guardrails),
        "dependencies": {"fastapi": "ok", "pydantic": "ok", "sqlite3": "ok"},
        "observability": observation.to_dict(),
    }


@app.get("/healthz/observability")
async def health_observability() -> Dict[str, object]:
    return build_runtime_observability_snapshot().to_dict()


@app.post("/insights/executive-brief", response_model=ExecutiveBriefResponse)
async def generate_executive_brief(request: InsightRequest) -> ExecutiveBriefResponse:
    start_time = datetime.now()
    brief_sections = _generate_deterministic_brief(request)
    processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
    return ExecutiveBriefResponse(
        request_id=str(uuid.uuid4()),
        generated_at=datetime.now(),
        company_profile=brief_sections["company_profile"],
        market_structure=brief_sections["market_structure"],
        competitor_landscape=brief_sections["competitor_landscape"],
        financial_quality=brief_sections["financial_quality"],
        product_capability=brief_sections["product_capability"],
        strategy_signals=brief_sections["strategy_signals"],
        risks=brief_sections["risks"],
        scenarios=brief_sections["scenarios"],
        evidence_references=brief_sections["evidence_references"],
        limitations=brief_sections["limitations"],
        confidence_score=0.85,
        processing_time_ms=processing_time_ms,
    )


def _generate_deterministic_brief(request: InsightRequest) -> Dict[str, Any]:
    company_name = request.company_name or "Company"
    industry = request.industry or "Technology"
    evidence_items = [
        EvidenceItem(source="internal_analysis", content=f"Analysis of {company_name} in {industry} sector", relevance_score=0.9),
        EvidenceItem(source="market_research", content=f"Industry benchmark data for {industry}", relevance_score=0.8),
        EvidenceItem(source="competitor_analysis", content=f"Competitive landscape analysis for {company_name}", relevance_score=0.85),
    ]
    risks = [
        RiskItem(category="market", description=f"Market volatility affecting {industry} sector", probability=0.7, impact=0.6, evidence_refs=[evidence_items[0].id]),
        RiskItem(category="operational", description="Supply chain disruptions", probability=0.5, impact=0.4, evidence_refs=[evidence_items[1].id]),
    ]
    scenarios = [
        ScenarioItem(name="Growth Scenario", description="Continued market expansion with favorable conditions", probability=0.4, impact_on_business=0.8),
        ScenarioItem(name="Base Scenario", description="Stable market performance with normal execution", probability=0.4, impact_on_business=0.5),
        ScenarioItem(name="Disruption Scenario", description="Technology disruption affects core business", probability=0.2, impact_on_business=0.9),
    ]
    return {
        "company_profile": BriefSection(title=f"Company Profile: {company_name}", content=f"{company_name} is a {industry} company with established market presence.", evidence_refs=[evidence_items[0].id]),
        "market_structure": BriefSection(title="Market Structure Analysis", content=f"The {industry} market shows consolidation trends with clear segment leaders.", evidence_refs=[evidence_items[1].id]),
        "competitor_landscape": BriefSection(title="Competitor Landscape", content=f"{company_name} competes with established players and emerging challengers.", evidence_refs=[evidence_items[2].id]),
        "financial_quality": BriefSection(title="Financial Quality Assessment", content="Financial metrics show stable cash flows with margin pressure.", evidence_refs=[evidence_items[0].id]),
        "product_capability": BriefSection(title="Product Capability Analysis", content="Product portfolio demonstrates a solid innovation pipeline.", evidence_refs=[evidence_items[1].id]),
        "strategy_signals": BriefSection(title="Strategy Signals", content="Strategic initiatives focus on digital transformation and market expansion.", evidence_refs=[evidence_items[2].id]),
        "risks": risks,
        "scenarios": scenarios,
        "evidence_references": evidence_items,
        "limitations": BriefSection(title="Analysis Limitations", content="Analysis is deterministic and based on available evidence inputs.", evidence_refs=[item.id for item in evidence_items], confidence_score=0.7),
    }
