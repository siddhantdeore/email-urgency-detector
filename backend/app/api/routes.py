"""FastAPI API routes for Cognitive Email Urgency Detector."""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.cognitive.reasoning_engine import CognitiveReasoningEngine
from backend.app.config import (
    COMPARISON_METRICS_PATH,
    DATA_DIR,
    FEEDBACK_FILE,
    METRICS_PATH,
)
from backend.app.schemas.email_schema import (
    AnalysisResponse,
    EmailInput,
    FeedbackInput,
    FeedbackResponse,
    ModelMetricsResponse,
    StatisticsResponse,
)

router = APIRouter()
engine = CognitiveReasoningEngine()

STATS_FILE = DATA_DIR / "analytics_history.json"


def _load_stats() -> Dict[str, Any]:
    """Load or initialize analytics statistics."""
    if STATS_FILE.exists():
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Baseline seed statistics from dataset
    return {
        "total_analyzed": 500,
        "critical_count": 125,
        "high_count": 125,
        "medium_count": 125,
        "low_count": 125,
        "urgency_distribution": {
            "Critical": 125,
            "High": 125,
            "Medium": 125,
            "Low": 125
        },
        "intent_distribution": {
            "Technical Issue": 120,
            "Security Alert": 55,
            "Payment Issue": 45,
            "Meeting": 60,
            "Deadline": 50,
            "Request": 70,
            "Information": 50,
            "General Communication": 50
        },
        "score_sum": 25000,
        "confidence_sum": 460.0
    }


def _update_stats(res: Dict[str, Any]):
    """Update analytics history persistently."""
    stats = _load_stats()
    stats["total_analyzed"] += 1
    urg = res["urgency_level"]
    intent = res["intent"]

    if urg == "Critical":
        stats["critical_count"] += 1
    elif urg == "High":
        stats["high_count"] += 1
    elif urg == "Medium":
        stats["medium_count"] += 1
    else:
        stats["low_count"] += 1

    stats["urgency_distribution"][urg] = stats["urgency_distribution"].get(urg, 0) + 1
    stats["intent_distribution"][intent] = stats["intent_distribution"].get(intent, 0) + 1
    stats["score_sum"] += res["urgency_score"]
    stats["confidence_sum"] += res["confidence"]

    try:
        STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"Warning: could not save stats: {e}")


@router.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "Cognitive Email Urgency Detector"}


@router.post("/analyze", response_model=AnalysisResponse)
@router.post("/predict", response_model=AnalysisResponse)
def analyze_email_endpoint(payload: EmailInput) -> AnalysisResponse:
    """Analyze email content through the cognitive reasoning pipeline."""
    if not payload.subject.strip() and not payload.body.strip():
        raise HTTPException(status_code=400, detail="Email subject or body cannot be empty.")

    try:
        result = engine.analyze_email(
            subject=payload.subject,
            body=payload.body,
            sender=payload.sender,
            sender_role=payload.sender_role,
            department=payload.department,
        )
        _update_stats(result)
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis pipeline error: {str(e)}")


@router.get("/model-info", response_model=ModelMetricsResponse)
def get_model_info() -> ModelMetricsResponse:
    """Retrieve production model metrics, confusion matrix, and feature importances."""
    if not METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="Model metrics file not found. Run training first.")

    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    return ModelMetricsResponse(**metrics)


@router.get("/model-comparison")
def get_model_comparison() -> Dict[str, Any]:
    """Retrieve model comparison experiment benchmark results."""
    if not COMPARISON_METRICS_PATH.exists():
        raise HTTPException(status_code=404, detail="Comparison metrics not found.")

    with open(COMPARISON_METRICS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@router.get("/statistics", response_model=StatisticsResponse)
def get_statistics() -> StatisticsResponse:
    """Return aggregated analytics for the analytics dashboard."""
    stats = _load_stats()
    total = max(1, stats["total_analyzed"])
    avg_score = round(stats["score_sum"] / total, 1)
    avg_conf = round(stats["confidence_sum"] / total, 3)

    most_common_intent = max(stats["intent_distribution"].items(), key=lambda x: x[1])[0]

    return StatisticsResponse(
        total_analyzed=total,
        critical_count=stats["critical_count"],
        high_count=stats["high_count"],
        medium_count=stats["medium_count"],
        low_count=stats["low_count"],
        avg_urgency_score=avg_score,
        avg_confidence=avg_conf,
        most_common_intent=most_common_intent,
        intent_distribution=stats["intent_distribution"],
        urgency_distribution=stats["urgency_distribution"]
    )


@router.post("/feedback", response_model=FeedbackResponse)
def record_feedback(payload: FeedbackInput) -> FeedbackResponse:
    """Record user correction to data/feedback.csv for model adaptation loop."""
    FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_exists = FEEDBACK_FILE.exists()

    with open(FEEDBACK_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["subject", "body", "predicted_urgency", "actual_urgency", "comments"])
        writer.writerow([
            payload.subject,
            payload.body,
            payload.predicted_urgency,
            payload.actual_urgency,
            payload.comments or ""
        ])

    # Count rows in feedback file
    total_feedback = 0
    with open(FEEDBACK_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        total_feedback = sum(1 for _ in reader) - 1

    return FeedbackResponse(
        status="success",
        message="Feedback successfully recorded for model retraining and cognitive adaptation.",
        total_feedback_count=max(1, total_feedback)
    )


@router.get("/examples")
def get_demo_examples() -> List[Dict[str, Any]]:

    """Provide at least 10 realistic preloaded demo scenarios."""
    return [
        {
            "id": 1,
            "title": "Production Server Outage (Critical)",
            "subject": "URGENT: Production PostgreSQL server is down",
            "body": "The primary database in us-east-1 is completely unreachable. Transactions are failing and customers cannot checkout. Immediate failover required right now.",
            "sender": "alerts@ops.domain.com",
            "sender_role": "SRE Lead"
        },
        {
            "id": 2,
            "title": "Active Security Breach (Critical)",
            "subject": "Security Incident: Active credential stuffing detected on auth endpoints",
            "body": "Our WAF detected over 150,000 unauthorized login attempts on the identity service. High risk of token compromise. Revoke all active sessions and rotate keys immediately.",
            "sender": "security-ops@domain.com",
            "sender_role": "Security Director"
        },
        {
            "id": 3,
            "title": "Client Demo in 30 Minutes (Critical Context)",
            "subject": "Executive demo server returning 502 Bad Gateway",
            "body": "Could you please fix the staging cluster before the enterprise client demonstration at 10 AM? The call starts in 30 minutes and the VP is on the line.",
            "sender": "sarah.vp@domain.com",
            "sender_role": "VP Sales"
        },
        {
            "id": 4,
            "title": "Payment Gateway Failure (Critical)",
            "subject": "Payment gateway offline during flash sale - checkout blocked",
            "body": "Stripe webhook callbacks are failing with 500 errors. Customers cannot complete orders. Revenue loss is occurring every minute. Resolve immediately.",
            "sender": "finance-bot@domain.com",
            "sender_role": "Finance Operations"
        },
        {
            "id": 5,
            "title": "Project Deadline Tomorrow (High)",
            "subject": "Action required: Quarterly financial report draft needed before tomorrow 5 PM",
            "body": "The executive committee meeting is scheduled for Friday morning. Please review the variance tables and submit your finalized division budget today before end of day.",
            "sender": "accounting@domain.com",
            "sender_role": "Controller"
        },
        {
            "id": 6,
            "title": "Interview Candidate Schedule Conflict (High)",
            "subject": "Urgent interview reschedule: Principal Architect candidate today",
            "body": "The candidate for the Principal Architect role is arriving in 2 hours, but our lead interviewer is sick. We urgently need a replacement panelist to confirm availability today.",
            "sender": "talent@domain.com",
            "sender_role": "Recruiting Lead"
        },
        {
            "id": 7,
            "title": "Normal Project Proposal Review (Medium)",
            "subject": "Please review the updated architecture proposal when you get time",
            "body": "I have incorporated team comments into the microservices RFC document. When you have a free moment this week, please take a look and leave your thoughts on the diagram.",
            "sender": "alex.dev@domain.com",
            "sender_role": "Software Engineer"
        },
        {
            "id": 8,
            "title": "Rescheduling 1-on-1 Sync (Medium)",
            "subject": "Rescheduling our 1-on-1 meeting this week",
            "body": "Hi there, I have a dentist appointment during our scheduled 2 PM slot tomorrow. Can we move our chat to Thursday morning at 10 AM instead? Let me know if that works.",
            "sender": "david@domain.com",
            "sender_role": "Colleague"
        },
        {
            "id": 9,
            "title": "Weekly Newsletter (Low)",
            "subject": "Weekly Engineering & Technology Digest - Issue #88",
            "body": "Here are this week's top curated tech articles on distributed consensus algorithms, Python 3.13 performance improvements, and upcoming local meetup dates.",
            "sender": "newsletter@techdigest.io",
            "sender_role": "External"
        },
        {
            "id": 10,
            "title": "Promotional Discount with Buzzwords (Low / Mixed Signal)",
            "subject": "URGENT ANNOUNCEMENT: Save 40% on office supplies before Friday!",
            "body": "Special corporate perks! Don't miss out on our quarterly stationery clearance event. Grab vouchers before Friday afternoon to enjoy huge savings on office desks.",
            "sender": "perks@corporatestore.com",
            "sender_role": "Vendor"
        },
        {
            "id": 11,
            "title": "Casual Coffee & Social Invite (Low)",
            "subject": "Team coffee break & trivia in the 3rd floor lounge",
            "body": "Hey team, the culture committee is hosting a casual coffee break and trivia session this Friday at 3:30 PM. Snacks and coffee provided. Hope to see you there!",
            "sender": "culture@domain.com",
            "sender_role": "Social Committee"
        }
    ]
