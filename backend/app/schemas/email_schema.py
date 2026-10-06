"""Pydantic schemas for request validation and response serialization."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field



class EmailInput(BaseModel):
    """Input payload for email analysis."""
    subject: str = Field(..., description="Subject line of the email")
    body: str = Field(..., description="Main content/body of the email")
    sender: Optional[str] = Field(None, description="Optional sender email address or name")
    sender_role: Optional[str] = Field(None, description="Optional role of sender (e.g., CTO, Client, Colleague)")
    department: Optional[str] = Field(None, description="Optional department (e.g., DevOps, Sales, HR)")


class CognitiveFactorBreakdown(BaseModel):
    """Detailed cognitive component scores out of 100."""
    ml_prediction: float = Field(..., description="ML classification probability score (0-100)")
    temporal_urgency: float = Field(..., description="Temporal urgency & deadline score (0-100)")
    business_impact: float = Field(..., description="Business & operational impact score (0-100)")
    urgency_language: float = Field(..., description="Explicit urgency keyword score (0-100)")
    context_severity: float = Field(..., description="Context & sentiment severity score (0-100)")


class HighlightedSpan(BaseModel):
    """Extracted phrase with category tag for UI highlighting."""
    text: str
    category: str = Field(..., description="Category: critical, temporal, business, or intent")
    reason: str


class AnalysisResponse(BaseModel):
    """Comprehensive cognitive urgency analysis response."""
    urgency_level: str = Field(..., description="Urgency classification: Critical, High, Medium, Low")
    is_urgent: bool = Field(..., description="Whether the email is considered urgent (High or Critical)")
    urgency_score: int = Field(..., description="Calculated urgency score (0-100)")
    confidence: float = Field(..., description="Overall confidence level (0.0 to 1.0)")
    intent: str = Field(..., description="Detected intent category")
    intent_confidence: float = Field(..., description="Confidence in detected intent (0.0 to 1.0)")
    important_phrases: List[str] = Field(default_factory=list, description="Key extracted phrases influencing decision")
    temporal_constraint: Optional[str] = Field(None, description="Detected deadline or time constraint, if any")
    business_impact: str = Field(..., description="Assessed impact: None, Low, Medium, High, or Critical")
    requires_immediate_attention: bool = Field(..., description="True if immediate human intervention is needed")
    recommended_action: str = Field(..., description="Prescribed action for the recipient")
    reasoning: List[str] = Field(default_factory=list, description="List of cognitive reasoning bullet points")
    detailed_explanation: str = Field(..., description="Natural language explanation of the decision")
    cognitive_breakdown: CognitiveFactorBreakdown = Field(..., description="Breakdown of individual cognitive factors")
    highlighted_html: str = Field(..., description="HTML-formatted email content with inline highlights")
    highlighted_spans: List[HighlightedSpan] = Field(default_factory=list, description="Structured highlight tokens")
    ml_probabilities: Dict[str, float] = Field(default_factory=dict, description="Raw ML class probabilities")


class FeedbackInput(BaseModel):
    """Feedback submitted by user to refine or retrain models."""
    subject: str
    body: str
    predicted_urgency: str
    actual_urgency: str
    comments: Optional[str] = None


class FeedbackResponse(BaseModel):
    status: str
    message: str
    total_feedback_count: int


class ModelMetricsResponse(BaseModel):
    """Evaluation metrics for the active ML model."""
    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    training_samples: int
    testing_samples: int
    confusion_matrix: List[List[int]]
    classes: List[str]
    classification_report: Dict
    top_features: Dict[str, List[Dict[str, Any]]]

    why_selected: str


class StatisticsResponse(BaseModel):
    """Aggregated usage and analytics statistics."""
    total_analyzed: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    avg_urgency_score: float
    avg_confidence: float
    most_common_intent: str
    intent_distribution: Dict[str, int]
    urgency_distribution: Dict[str, int]

