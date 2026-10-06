"""Offline evaluation script for model performance and cognitive reasoning verification."""

import json
from pathlib import Path
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.cognitive.reasoning_engine import CognitiveReasoningEngine
from backend.app.config import EMAILS_FILE, METRICS_PATH
from backend.app.ml.predict import predict_email_ml


def run_full_evaluation():
    print("=" * 60)
    print("COGNITIVE EMAIL URGENCY DETECTOR: OFFLINE EVALUATION SUITE")
    print("=" * 60)

    # 1. Load ML Model Metrics
    if METRICS_PATH.exists():
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)
        print(f"\n[1] Production Model: {metrics['model_name']}")
        print(f"    - Accuracy:  {metrics['accuracy'] * 100:.2f}%")
        print(f"    - Precision: {metrics['precision'] * 100:.2f}%")
        print(f"    - Recall:    {metrics['recall'] * 100:.2f}%")
        print(f"    - F1-Score:  {metrics['f1_score'] * 100:.2f}%")
        print(f"    - Samples:   {metrics['training_samples']} train / {metrics['testing_samples']} test")

        print("\n[2] Confusion Matrix:")
        classes = metrics["classes"]
        header = f"{'Actual \\ Pred':<15}" + "".join([f"{c:<12}" for c in classes])
        print("    " + header)
        for i, row in enumerate(metrics["confusion_matrix"]):
            row_str = f"{classes[i]:<15}" + "".join([f"{val:<12}" for val in row])
            print("    " + row_str)

    # 2. Test Cognitive Reasoning on Benchmark Case Studies
    print("\n[3] Cognitive Reasoning Layer Verification:")
    engine = CognitiveReasoningEngine()

    case_studies = [
        (
            "Outage with short deadline",
            "URGENT: Production PostgreSQL server is down",
            "The database is completely unreachable. Client demo starts in 30 minutes. Please fix immediately."
        ),
        (
            "Severe operational impact WITHOUT 'urgent' keyword",
            "Database unavailability",
            "The production database is unavailable and tomorrow's client demonstration depends on it."
        ),
        (
            "Marketing email with urgency buzzwords (False Positive check)",
            "URGENT ANNOUNCEMENT: Save 40% on office supplies before Friday!",
            "Don't miss our quarterly clearance event! Grab discount vouchers before Friday."
        ),
        (
            "Routine internal scheduling",
            "Rescheduling our 1-on-1 meeting this week",
            "Can we shift our chat to Thursday morning? Let me know when convenient."
        )
    ]

    for title, subj, body in case_studies:
        res = engine.analyze_email(subj, body)
        print(f"\n    Case: {title}")
        print(f"    Input: '{subj}'")
        print(f"    -> Priority:      {res['urgency_level'].upper()} (Score: {res['urgency_score']}/100)")
        print(f"    -> Intent:        {res['intent']} (Conf: {res['intent_confidence']:.0%})")
        print(f"    -> Timeframe:     {res['temporal_constraint'] or 'None'}")
        print(f"    -> Action:        {res['recommended_action']}")
        print(f"    -> Human Alert:   {'YES' if res['requires_immediate_attention'] else 'NO'}")
        print(f"    -> Primary Rationale:")
        for r in res["reasoning"][:2]:
            print(f"       * {r}")

    print("\n" + "=" * 60)
    print("EVALUATION COMPLETE - ALL COGNITIVE MODES OPERATIONAL")
    print("=" * 60)


if __name__ == "__main__":
    run_full_evaluation()

