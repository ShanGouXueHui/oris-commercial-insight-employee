import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
    """Test basic health endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data

def test_healthz_details():
    """Test health details endpoint"""
    response = client.get("/healthz/details")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "service" in data
    assert "dependencies" in data
    assert data["dependencies"]["fastapi"] == "ok"
    assert data["dependencies"]["pydantic"] == "ok"