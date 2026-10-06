"""Machine Learning inference module for Urgency and Intent prediction."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib
import numpy as np

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.config import INTENT_MODEL_PATH, TFIDF_VECTORIZER_PATH, URGENCY_MODEL_PATH
from backend.app.ml.preprocess import clean_text, prepare_combined_text

_URGENCY_MODEL = None
_VECTORIZER = None
_INTENT_MODEL = None


def get_models():
    """Lazy load models with memory caching."""
    global _URGENCY_MODEL, _VECTORIZER, _INTENT_MODEL
    if _URGENCY_MODEL is None and URGENCY_MODEL_PATH.exists():
        _URGENCY_MODEL = joblib.load(URGENCY_MODEL_PATH)
    if _VECTORIZER is None and TFIDF_VECTORIZER_PATH.exists():
        _VECTORIZER = joblib.load(TFIDF_VECTORIZER_PATH)
    if _INTENT_MODEL is None and INTENT_MODEL_PATH.exists():
        _INTENT_MODEL = joblib.load(INTENT_MODEL_PATH)
    return _URGENCY_MODEL, _VECTORIZER, _INTENT_MODEL


def predict_email_ml(subject: str, body: str) -> Dict[str, Any]:
    """Execute ML inference using TF-IDF and Logistic Regression."""
    urgency_model, vectorizer, intent_model = get_models()

    if not urgency_model or not vectorizer:
        raise RuntimeError("ML models have not been trained yet. Please run backend/app/ml/train.py.")

    raw_combined = prepare_combined_text(subject, body)
    cleaned = clean_text(raw_combined)

    # Feature transformation
    X = vectorizer.transform([cleaned])

    # Urgency prediction & probabilities
    probabilities = urgency_model.predict_proba(X)[0]
    classes = list(urgency_model.classes_)
    prob_dict = {cls: round(float(prob), 4) for cls, prob in zip(classes, probabilities)}

    top_idx = int(np.argmax(probabilities))
    predicted_urgency = classes[top_idx]
    confidence = float(probabilities[top_idx])

    # Explainability: Extract top contributing tokens for the predicted class
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = urgency_model.coef_[top_idx]
    nonzero_indices = X.nonzero()[1]

    feature_contributions = []
    for idx in nonzero_indices:
        tfidf_val = X[0, idx]
        weight = coefs[idx]
        contribution = tfidf_val * weight
        if contribution > 0:
            feature_contributions.append({
                "word": feature_names[idx],
                "score": round(float(contribution), 4)
            })

    # Sort descending by contribution
    feature_contributions = sorted(feature_contributions, key=lambda x: x["score"], reverse=True)[:8]

    # Intent prediction
    intent = "General Communication"
    intent_confidence = 0.50
    if intent_model:
        try:
            intent_probs = intent_model.predict_proba(X)[0]
            intent_idx = int(np.argmax(intent_probs))
            intent = intent_model.classes_[intent_idx]
            intent_confidence = round(float(intent_probs[intent_idx]), 4)
        except Exception:
            intent = intent_model.predict(X)[0]
            intent_confidence = 0.85

    return {
        "predicted_class": predicted_urgency,
        "probabilities": prob_dict,
        "confidence": round(confidence, 4),
        "intent": intent,
        "intent_confidence": intent_confidence,
        "top_features": feature_contributions,
        "cleaned_text": cleaned
    }

