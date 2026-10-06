"""Integration tests for FastAPI endpoints."""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint_critical():
    payload = {
        "subject": "URGENT: Production server is down",
        "body": "Immediate attention required. The cluster is unresponsive and client demo starts in 30 minutes.",
        "sender": "cto@company.com",
        "sender_role": "CTO"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["urgency_level"] == "Critical"
    assert data["urgency_score"] >= 76
    assert data["is_urgent"] is True
    assert data["intent"] == "Technical Issue"
    assert "recommended_action" in data
    assert "cognitive_breakdown" in data
    assert len(data["reasoning"]) > 0
    assert "highlighted_html" in data


def test_analyze_empty_payload_validation():
    payload = {"subject": "   ", "body": "   "}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400


def test_model_info_endpoint():
    response = client.get("/api/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "accuracy" in data
    assert "confusion_matrix" in data
    assert "top_features" in data
    assert data["accuracy"] > 0.90


def test_statistics_endpoint():
    response = client.get("/api/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyzed" in data
    assert "critical_count" in data
    assert "urgency_distribution" in data


def test_feedback_endpoint():
    payload = {
        "subject": "Test feedback subject",
        "body": "Test feedback body",
        "predicted_urgency": "High",
        "actual_urgency": "Critical",
        "comments": "Critical due to immediate executive presence."
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["total_feedback_count"] >= 1


def test_examples_endpoint():
    response = client.get("/api/examples")
    assert response.status_code == 200
    examples = response.json()
    assert isinstance(examples, list)
    assert len(examples) >= 10

