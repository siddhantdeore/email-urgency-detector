"""Unit tests for Cognitive Reasoning Engine, Temporal Analyzer, and Intent Detector."""

from pathlib import Path
import pytest

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.cognitive.intent_detector import IntentDetector
from backend.app.cognitive.reasoning_engine import CognitiveReasoningEngine
from backend.app.cognitive.temporal_analyzer import TemporalAnalyzer
from backend.app.cognitive.urgency_detector import UrgencySignalDetector


@pytest.fixture
def engine():
    return CognitiveReasoningEngine()


@pytest.fixture
def temporal():
    return TemporalAnalyzer()


@pytest.fixture
def urgency():
    return UrgencySignalDetector()


@pytest.fixture
def intent():
    return IntentDetector()


def test_temporal_analyzer_tiers(temporal):
    # Tier 1: Immediate / 30 mins
    res1 = temporal.analyze("Client demo starts in 30 minutes, please help immediately!")
    assert res1["temporal_score"] >= 90.0
    assert res1["urgency_tier"] == "Critical"
    assert res1["detected_constraint"] is not None

    # Tier 2: Today / before 5 PM
    res2 = temporal.analyze("Please submit your report before 5 PM today.")
    assert 75.0 <= res2["temporal_score"] <= 85.0
    assert res2["urgency_tier"] == "High"

    # Tier 3: Tomorrow
    res3 = temporal.analyze("Meeting rescheduled to tomorrow morning.")
    assert 60.0 <= res3["temporal_score"] <= 70.0

    # Low / No rush
    res4 = temporal.analyze("Take a look next month when you have time, no rush.")
    assert res4["temporal_score"] <= 15.0


def test_urgency_signals_and_business_impact(urgency):
    text = "Critical outage on our core database. Catastrophic revenue loss occurring."
    urg_res = urgency.analyze_urgency_signals(text)
    assert urg_res["urgency_language_score"] >= 70.0
    assert len(urg_res["critical_matches"]) > 0

    biz_res = urgency.analyze_business_impact(text)
    assert biz_res["impact_level"] == "Critical"
    assert biz_res["impact_score"] >= 90.0


def test_intent_detection(intent):
    sec_intent, sec_conf, _ = intent.detect("Security alert", "Active unauthorized credential stuffing detected", "Security Alert", 0.9)
    assert sec_intent == "Security Alert"
    assert sec_conf > 0.8

    pay_intent, _, _ = intent.detect("Billing alert", "Stripe payment webhook 500 error", "Payment Issue", 0.88)
    assert pay_intent == "Payment Issue"

    meet_intent, _, _ = intent.detect("Sync", "Rescheduling our 1-on-1 meeting tomorrow", "Meeting", 0.85)
    assert meet_intent == "Meeting"


def test_reasoning_production_critical(engine):
    subject = "URGENT: Production server is down"
    body = "Please resolve this issue immediately. Client demo starts in 30 minutes."
    res = engine.analyze_email(subject, body)

    assert res["urgency_level"] == "Critical"
    assert res["urgency_score"] >= 76
    assert res["is_urgent"] is True
    assert res["requires_immediate_attention"] is True
    assert res["intent"] == "Technical Issue"
    assert len(res["reasoning"]) >= 3
    assert "hl-critical" in res["highlighted_html"]


def test_reasoning_contextual_severity_without_urgent_keyword(engine):
    """Cognitive test: Severe business context without the literal word 'urgent'."""
    subject = "Database unavailability"
    body = "The production database is unavailable and tomorrow's client demonstration depends on it."
    res = engine.analyze_email(subject, body)

    # Should be High or Critical despite missing the word "urgent"
    assert res["urgency_level"] in ["High", "Critical"]
    assert res["urgency_score"] >= 60
    assert res["business_impact"] in ["Critical", "High"]



def test_reasoning_marketing_hype_suppression(engine):
    """Cognitive test: Promotional email with 'urgent' buzzword suppressed to Low."""
    subject = "URGENT ANNOUNCEMENT: Save 30% on office stationery this Friday!"
    body = "Special corporate perks discount! Don't miss our quarterly office clearance sale."
    res = engine.analyze_email(subject, body)

    assert res["urgency_level"] in ["Low", "Medium"]
    assert res["urgency_score"] <= 40
    assert any("marketing" in r.lower() or "hype" in r.lower() for r in res["reasoning"])


def test_reasoning_empty_or_edge_input(engine):
    # Minimal input
    res = engine.analyze_email("Hello", "Thanks")
    assert res["urgency_level"] in ["Low", "Medium"]
    assert res["urgency_score"] <= 50
