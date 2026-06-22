from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

app = FastAPI(
    title="ORIS Commercial Insight Employee API",
    description="Standalone commercial insight employee product API",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
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

# Health endpoints
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/healthz/details")
async def health_details():
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "0.1.0",
        "service": "ORIS Commercial Insight Employee API",
        "database": "not_configured",
        "cache": "not_configured",
        "dependencies": {
            "fastapi": "ok",
            "pydantic": "ok"
        }
    }

# Executive brief endpoint
@app.post("/insights/executive-brief", response_model=ExecutiveBriefResponse)
async def generate_executive_brief(request: InsightRequest):
    """Generate a deterministic executive brief based on insight request"""
    start_time = datetime.now()
    
    # Deterministic stub workflow
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
        processing_time_ms=processing_time_ms
    )

def _generate_deterministic_brief(request: InsightRequest) -> Dict[str, Any]:
    """Generate deterministic brief sections based on request"""
    company_name = request.company_name or "Company"
    industry = request.industry or "Technology"
    
    # Generate deterministic evidence items
    evidence_items = [
        EvidenceItem(
            source="internal_analysis",
            content=f"Analysis of {company_name} in {industry} sector",
            relevance_score=0.9,
            metadata={"type": "financial", "period": "2024"}
        ),
        EvidenceItem(
            source="market_research",
            content=f"Industry benchmark data for {industry}",
            relevance_score=0.8,
            metadata={"type": "market", "source": "gartner"}
        ),
        EvidenceItem(
            source="competitor_analysis",
            content=f"Competitive landscape analysis for {company_name}",
            relevance_score=0.85,
            metadata={"type": "competitive", "scope": "regional"}
        )
    ]
    
    # Generate deterministic risk items
    risks = [
        RiskItem(
            category="market",
            description=f"Market volatility affecting {industry} sector",
            probability=0.7,
            impact=0.6,
            mitigation_strategy="Diversify revenue streams",
            evidence_refs=[evidence_items[0].id]
        ),
        RiskItem(
            category="operational",
            description="Supply chain disruptions",
            probability=0.5,
            impact=0.4,
            mitigation_strategy="Multiple supplier contracts",
            evidence_refs=[evidence_items[1].id]
        ),
        RiskItem(
            category="financial",
            description="Currency fluctuation risks",
            probability=0.6,
            impact=0.5,
            mitigation_strategy="Hedging strategies",
            evidence_refs=[evidence_items[2].id]
        )
    ]
    
    # Generate deterministic scenario items
    scenarios = [
        ScenarioItem(
            name="Growth Scenario",
            description="Continued market expansion with favorable conditions",
            probability=0.4,
            impact_on_business=0.8,
            key_drivers=["Market growth", "Innovation", "Strong leadership"],
            outcomes=["Increased market share", "Higher profitability"]
        ),
        ScenarioItem(
            name="Stagnation Scenario",
            description="Market plateau with limited growth opportunities",
            probability=0.35,
            impact_on_business=0.4,
            key_drivers=["Market saturation", "Increased competition"],
            outcomes=["Stable performance", "Focus on efficiency"]
        ),
        ScenarioItem(
            name="Disruption Scenario",
            description="Technological disruption impacting core business",
            probability=0.25,
            impact_on_business=0.9,
            key_drivers=["New entrants", "Technology shifts"],
            outcomes=["Need for transformation", "Potential decline"]
        )
    ]
    
    return {
        "company_profile": BriefSection(
            title=f"Company Profile: {company_name}",
            content=f"{company_name} is a {industry} company with established market presence. Key strengths include strong brand recognition, experienced leadership team, and robust product portfolio.",
            evidence_refs=[evidence_items[0].id],
            confidence_score=0.85
        ),
        "market_structure": BriefSection(
            title="Market Structure Analysis",
            content=f"The {industry} market shows consolidation trends with clear segment leaders. Market size projected to grow at 5-7% CAGR over next 3 years. Key dynamics include regulatory changes and technological adoption curves.",
            evidence_refs=[evidence_items[1].id],
            confidence_score=0.8
        ),
        "competitor_landscape": BriefSection(
            title="Competitor Landscape",
            content=f"Direct competitors include established players and emerging challengers. Market share concentration varies by segment. {company_name} holds moderate position with opportunities in underserved niches.",
            evidence_refs=[evidence_items[2].id],
            confidence_score=0.75
        ),
        "financial_quality": BriefSection(
            title="Financial Quality Assessment",
            content="Financial metrics show stable cash flows with moderate leverage. Revenue growth consistent but margins under pressure from cost inflation. Working capital management needs improvement.",
            evidence_refs=[evidence_items[0].id],
            confidence_score=0.8
        ),
        "product_capability": BriefSection(
            title="Product Capability Analysis",
            content="Product portfolio demonstrates solid innovation pipeline. Core offerings remain competitive but some areas need modernization. Customer satisfaction scores average to above industry benchmarks.",
            evidence_refs=[evidence_items[1].id],
            confidence_score=0.75
        ),
        "strategy_signals": BriefSection(
            title="Strategy Signals",
            content="Strategic initiatives focus on digital transformation and market expansion. Investment in R&D shows positive trajectory. Leadership communicates clear long-term vision with milestone targets.",
            evidence_refs=[evidence_items[2].id],
            confidence_score=0.85
        ),
        "risks": risks,
        "scenarios": scenarios,
        "evidence_references": evidence_items,
        "limitations": BriefSection(
            title="Analysis Limitations",
            content="Analysis based on available public data and internal estimates. External factors like geopolitical events and regulatory changes not fully quantified. Forward-looking statements involve inherent uncertainties.",
            evidence_refs=[evidence_items[0].id, evidence_items[1].id, evidence_items[2].id],
            confidence_score=0.7
        )
    }