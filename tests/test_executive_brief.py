import pytest
from fastapi.testclient import TestClient
from app.main import app, InsightRequest
import json

client = TestClient(app)

def test_executive_brief_basic():
    """Test executive brief endpoint with basic request"""
    request_data = {
        "company_name": "Test Company",
        "industry": "Technology",
        "focus_areas": ["financial", "market"],
        "time_horizon": "2024-2026"
    }
    
    response = client.post("/insights/executive-brief", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "id" in data
    assert "request_id" in data
    assert "generated_at" in data
    assert "company_profile" in data
    assert "market_structure" in data
    assert "competitor_landscape" in data
    assert "financial_quality" in data
    assert "product_capability" in data
    assert "strategy_signals" in data
    assert "risks" in data
    assert "scenarios" in data
    assert "evidence_references" in data
    assert "limitations" in data
    assert "confidence_score" in data
    assert "processing_time_ms" in data
    
    # Check data types
    assert isinstance(data["company_profile"], dict)
    assert isinstance(data["market_structure"], dict)
    assert isinstance(data["competitor_landscape"], dict)
    assert isinstance(data["financial_quality"], dict)
    assert isinstance(data["product_capability"], dict)
    assert isinstance(data["strategy_signals"], dict)
    assert isinstance(data["risks"], list)
    assert isinstance(data["scenarios"], list)
    assert isinstance(data["evidence_references"], list)
    assert isinstance(data["limitations"], dict)
    
    # Check confidence score range
    assert 0.0 <= data["confidence_score"] <= 1.0
    
    # Check processing time is reasonable
    assert data["processing_time_ms"] >= 0

def test_executive_brief_minimal():
    """Test executive brief endpoint with minimal request"""
    request_data = {
        "company_name": "Minimal Company"
    }
    
    response = client.post("/insights/executive-brief", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Should still generate complete brief
    assert "company_profile" in data
    assert "market_structure" in data
    assert "competitor_landscape" in data
    assert "financial_quality" in data
    assert "product_capability" in data
    assert "strategy_signals" in data
    assert "risks" in data
    assert "scenarios" in data
    assert "evidence_references" in data
    assert "limitations" in data

def test_executive_brief_with_all_fields():
    """Test executive brief endpoint with all optional fields"""
    request_data = {
        "company_name": "Complete Company",
        "industry": "Healthcare",
        "focus_areas": ["strategy", "operations", "finance"],
        "time_horizon": "2025-2028",
        "user_id": "test_user_123",
        "evidence_sources": ["internal", "external", "market_research"]
    }
    
    response = client.post("/insights/executive-brief", json=request_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify request_id is generated
    assert data["request_id"] is not None
    assert len(data["request_id"]) > 0
    
    # Verify risks have required structure
    for risk in data["risks"]:
        assert "id" in risk
        assert "category" in risk
        assert "description" in risk
        assert "probability" in risk
        assert "impact" in risk
        assert 0.0 <= risk["probability"] <= 1.0
        assert 0.0 <= risk["impact"] <= 1.0
    
    # Verify scenarios have required structure
    for scenario in data["scenarios"]:
        assert "id" in scenario
        assert "name" in scenario
        assert "description" in scenario
        assert "probability" in scenario
        assert "impact_on_business" in scenario
        assert 0.0 <= scenario["probability"] <= 1.0
        assert 0.0 <= scenario["impact_on_business"] <= 1.0
    
    # Verify evidence references have required structure
    for evidence in data["evidence_references"]:
        assert "id" in evidence
        assert "source" in evidence
        assert "content" in evidence
        assert "relevance_score" in evidence
        assert 0.0 <= evidence["relevance_score"] <= 1.0