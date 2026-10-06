"""Configuration settings for Cognitive Email Urgency Detector."""

from pathlib import Path
from typing import Dict, Tuple
from pydantic import BaseModel

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
FEEDBACK_FILE = DATA_DIR / "feedback.csv"
EMAILS_FILE = DATA_DIR / "emails.csv"
PROCESSED_FILE = DATA_DIR / "processed_emails.csv"

# Model artifact paths
URGENCY_MODEL_PATH = MODELS_DIR / "urgency_model.pkl"
TFIDF_VECTORIZER_PATH = MODELS_DIR / "tfidf_vectorizer.pkl"
INTENT_MODEL_PATH = MODELS_DIR / "intent_model.pkl"
METRICS_PATH = MODELS_DIR / "model_metrics.json"
COMPARISON_METRICS_PATH = MODELS_DIR / "model_comparison.json"

# Cognitive Scoring Weights (Configurable)
class CognitiveWeights:
    """Configurable weights for the cognitive reasoning urgency score."""
    def __init__(
        self,
        ml_weight: float = 0.40,
        temporal_weight: float = 0.20,
        business_weight: float = 0.20,
        urgency_lang_weight: float = 0.10,
        context_severity_weight: float = 0.10,
    ):
        self.ml_weight = ml_weight
        self.temporal_weight = temporal_weight
        self.business_weight = business_weight
        self.urgency_lang_weight = urgency_lang_weight
        self.context_severity_weight = context_severity_weight

    def to_dict(self) -> Dict[str, float]:
        return {
            "ml_weight": self.ml_weight,
            "temporal_weight": self.temporal_weight,
            "business_weight": self.business_weight,
            "urgency_lang_weight": self.urgency_lang_weight,
            "context_severity_weight": self.context_severity_weight,
        }

DEFAULT_WEIGHTS = CognitiveWeights()

# Urgency Score Ranges (0 - 100)
URGENCY_THRESHOLDS: Dict[str, Tuple[int, int]] = {
    "Low": (0, 25),
    "Medium": (26, 50),
    "High": (51, 75),
    "Critical": (76, 100),
}

# Supported Intent Categories
INTENTS = [
    "Technical Issue",
    "Security Alert",
    "Payment Issue",
    "Meeting",
    "Deadline",
    "Request",
    "Complaint",
    "Job/Interview",
    "Academic",
    "Information",
    "General Communication",
]

