"""Unit tests for ML models, vectorizer, and preprocessing."""

from pathlib import Path
import pytest

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.ml.predict import predict_email_ml
from backend.app.ml.preprocess import clean_text, extract_structural_features, prepare_combined_text


def test_clean_text():
    raw = "URGENT: Please visit https://example.com and email dev@platform.com immediately!!!"
    cleaned = clean_text(raw)
    assert "urgent" in cleaned
    assert "immediately" in cleaned
    assert "https" not in cleaned
    assert "example.com" not in cleaned


def test_extract_structural_features():
    subject = "[URGENT] Database CRASH!!!"
    body = "Is anyone looking at this right now?! Need immediate fix."
    features = extract_structural_features(subject, body)
    assert features["exclamation_count"] >= 3
    assert features["urgent_punct_patterns"] >= 1
    assert features["subject_has_alert_tag"] == 1.0
    assert features["upper_ratio"] > 0.1


def test_predict_email_ml_critical():
    subject = "Production database cluster down"
    body = "The primary database is completely unreachable. Transactions are failing."
    res = predict_email_ml(subject, body)
    assert res["predicted_class"] in ["Critical", "High"]
    assert "Critical" in res["probabilities"]
    assert "High" in res["probabilities"]
    assert "Medium" in res["probabilities"]
    assert "Low" in res["probabilities"]
    # Probability distribution should sum to approximately 1.0
    total_prob = sum(res["probabilities"].values())
    assert 0.99 <= total_prob <= 1.01
    assert res["confidence"] > 0.4
    assert len(res["top_features"]) > 0


def test_predict_email_ml_edge_cases():
    # Very short email
    short_res = predict_email_ml("Hi", "Quick question")
    assert short_res["predicted_class"] in ["Medium", "Low", "High", "Critical"]
    assert short_res["confidence"] > 0.0

    # Long email
    long_body = "Routine project status update with multiple paragraphs and notes. " * 80
    long_res = predict_email_ml("Weekly update", long_body)
    assert long_res["predicted_class"] in ["Medium", "Low"]

