"""Train production ML models for Urgency and Intent detection.

Uses TF-IDF + Logistic Regression, performs train/test evaluation,
extracts feature importance coefficients, saves models, and updates metrics.
"""

import json
from pathlib import Path
from typing import Dict, List
import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

import sys
# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.config import (
    EMAILS_FILE,
    FEEDBACK_FILE,
    INTENT_MODEL_PATH,
    METRICS_PATH,
    MODELS_DIR,
    PROCESSED_FILE,
    TFIDF_VECTORIZER_PATH,
    URGENCY_MODEL_PATH,
)

from backend.app.ml.evaluate import evaluate_classifier
from backend.app.ml.preprocess import clean_text, prepare_combined_text


def train_models():
    """Main training routine for Urgency and Intent classifiers."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if not EMAILS_FILE.exists():
        raise FileNotFoundError(f"Training data not found at {EMAILS_FILE}")

    # Load dataset
    df = pd.read_csv(EMAILS_FILE)

    # Incorporate user feedback if available (Cognitive Adaptation Loop)
    if FEEDBACK_FILE.exists():
        try:
            feedback_df = pd.read_csv(FEEDBACK_FILE)
            if not feedback_df.empty and "actual_urgency" in feedback_df.columns:
                feedback_formatted = pd.DataFrame({
                    "email_id": [f"FB-{i:03d}" for i in range(len(feedback_df))],
                    "subject": feedback_df["subject"],
                    "body": feedback_df["body"],
                    "urgency_level": feedback_df["actual_urgency"],
                    "intent": feedback_df.get("intent", ["Request"] * len(feedback_df))
                })
                df = pd.concat([df, feedback_formatted], ignore_index=True)
                print(f"Incorporated {len(feedback_formatted)} feedback examples into training.")
        except Exception as e:
            print(f"Warning: could not load feedback file: {e}")

    # Preprocess text
    df["combined_raw"] = [
        prepare_combined_text(s, b) for s, b in zip(df["subject"].fillna(""), df["body"].fillna(""))
    ]
    df["processed_text"] = [clean_text(t) for t in df["combined_raw"]]

    # Save processed dataset
    df[["email_id", "subject", "body", "processed_text", "urgency_level", "intent"]].to_csv(
        PROCESSED_FILE, index=False
    )
    print(f"Saved processed dataset to {PROCESSED_FILE}")

    # Split dataset for Urgency Model
    class_order = ["Critical", "High", "Medium", "Low"]
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df["processed_text"].tolist(),
        df["urgency_level"].tolist(),
        test_size=0.2,
        random_state=42,
        stratify=df["urgency_level"].tolist()
    )

    # 1. Fit TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=3000,
        sublinear_tf=True,
        min_df=2
    )
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)

    # 2. Train Urgency Classifier (Logistic Regression)
    urgency_model = LogisticRegression(
        C=2.0,
        max_iter=600,
        random_state=42,
        solver="lbfgs"
    )
    urgency_model.fit(X_train, y_train)

    # Evaluate Urgency Model
    y_pred = urgency_model.predict(X_test)
    urgency_metrics = evaluate_classifier(y_test, y_pred, labels=class_order)

    # 3. Train Intent Classifier
    intent_labels = df["intent"].fillna("General Communication").tolist()
    X_train_int_raw, X_test_int_raw, y_train_int, y_test_int = train_test_split(
        df["processed_text"].tolist(),
        intent_labels,
        test_size=0.2,
        random_state=42,
        stratify=intent_labels
    )
    X_train_int = vectorizer.transform(X_train_int_raw)
    X_test_int = vectorizer.transform(X_test_int_raw)

    intent_model = LogisticRegression(
        C=1.5,
        max_iter=600,
        random_state=42
    )
    intent_model.fit(X_train_int, y_train_int)
    unique_intents = sorted(list(set(intent_labels)))
    intent_pred = intent_model.predict(X_test_int)
    intent_metrics = evaluate_classifier(y_test_int, intent_pred, labels=unique_intents)

    # 4. Extract Top Informative Features per Urgency Class (Explainability)
    feature_names = np.array(vectorizer.get_feature_names_out())
    top_features_per_class: Dict[str, List[Dict[str, float]]] = {}

    for i, cls in enumerate(urgency_model.classes_):
        coefs = urgency_model.coef_[i]
        top_indices = np.argsort(coefs)[-10:][::-1]
        top_features_per_class[cls] = [
            {"feature": feature_names[idx], "weight": round(float(coefs[idx]), 3)}
            for idx in top_indices
        ]

    # Save model artifacts
    joblib.dump(urgency_model, URGENCY_MODEL_PATH)
    joblib.dump(vectorizer, TFIDF_VECTORIZER_PATH)
    joblib.dump(intent_model, INTENT_MODEL_PATH)

    # Save comprehensive metrics JSON
    metrics_summary = {
        "model_name": "TF-IDF + Multinomial Logistic Regression",
        "accuracy": urgency_metrics["accuracy"],
        "precision": urgency_metrics["precision"],
        "recall": urgency_metrics["recall"],
        "f1_score": urgency_metrics["f1_score"],
        "training_samples": len(X_train_raw),
        "testing_samples": len(X_test_raw),
        "classes": class_order,
        "confusion_matrix": urgency_metrics["confusion_matrix"],
        "classification_report": urgency_metrics["classification_report"],
        "top_features": top_features_per_class,
        "intent_accuracy": intent_metrics["accuracy"],
        "intent_f1": intent_metrics["f1_score"],
        "why_selected": (
            "Multinomial Logistic Regression with sublinear TF-IDF features provides state-of-the-art "
            "classification accuracy for text priority tasks while preserving full mathematical explainability. "
            "Unlike opaque deep neural networks, its learned weights directly quantify feature attribution, "
            "enabling transparent reasoning explanations and instant low-latency predictions."
        )
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    print("\n=== URGENCY MODEL TRAINING COMPLETE ===")
    print(f"Accuracy:  {urgency_metrics['accuracy']:.4f}")
    print(f"Precision: {urgency_metrics['precision']:.4f}")
    print(f"Recall:    {urgency_metrics['recall']:.4f}")
    print(f"F1-Score:  {urgency_metrics['f1_score']:.4f}")
    print(f"Saved artifacts to {MODELS_DIR}")
    return metrics_summary


if __name__ == "__main__":
    train_models()

