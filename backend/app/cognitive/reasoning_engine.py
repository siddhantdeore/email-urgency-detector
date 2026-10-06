"""Cognitive Reasoning Engine.

Fuses Machine Learning probabilities, temporal constraints, business impact,
urgency lexicon, typographical severity, and sender metadata into a unified
cognitive priority judgment with explainable reasoning.
"""

import html
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.cognitive.intent_detector import IntentDetector
from backend.app.cognitive.temporal_analyzer import TemporalAnalyzer
from backend.app.cognitive.urgency_detector import UrgencySignalDetector
from backend.app.config import DEFAULT_WEIGHTS, URGENCY_THRESHOLDS
from backend.app.ml.predict import predict_email_ml


class CognitiveReasoningEngine:
    """Multi-stage Cognitive Reasoning Engine simulating human expert triage."""

    def __init__(self):
        self.temporal_analyzer = TemporalAnalyzer()
        self.urgency_detector = UrgencySignalDetector()
        self.intent_detector = IntentDetector()

    def analyze_email(
        self,
        subject: str,
        body: str,
        sender: Optional[str] = None,
        sender_role: Optional[str] = None,
        department: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform end-to-end cognitive reasoning on the given email."""
        combined_text = f"{subject} {body}".strip()

        # Step 1: Statistical NLP / Machine Learning Inference
        ml_result = predict_email_ml(subject, body)
        ml_probs = ml_result["probabilities"]
        ml_predicted_class = ml_result["predicted_class"]

        # Step 2: Temporal & Deadline Perception
        temporal_result = self.temporal_analyzer.analyze(combined_text)
        temporal_score = temporal_result["temporal_score"]
        temporal_constraint = temporal_result["detected_constraint"]

        # Step 3: Urgency Lexicon & Context Severity
        urgency_result = self.urgency_detector.analyze_urgency_signals(combined_text)
        urgency_lang_score = urgency_result["urgency_language_score"]
        context_severity_score = urgency_result["context_severity_score"]

        # Step 4: Business Impact Perception
        business_result = self.urgency_detector.analyze_business_impact(combined_text)
        business_impact_level = business_result["impact_level"]
        business_impact_score = business_result["impact_score"]

        # Step 5: Intent Understanding
        intent_label, intent_conf, intent_keywords = self.intent_detector.detect(
            subject=subject,
            body=body,
            ml_intent=ml_result["intent"],
            ml_confidence=ml_result["intent_confidence"]
        )

        # Step 6: Sender Role / Metadata Perception (Optional cognitive modifier)
        sender_bonus = 0.0
        role_notes = []
        if sender_role:
            role_lower = sender_role.lower()
            if any(r in role_lower for r in ["ceo", "cto", "cio", "vp", "director", "executive"]):
                sender_bonus += 10.0
                role_notes.append(f"High-priority sender hierarchy detected ({sender_role})")
            elif "client" in role_lower or "customer" in role_lower:
                sender_bonus += 8.0
                role_notes.append(f"External client priority detected ({sender_role})")

        # Step 7: Cognitive Synthesis & Dynamic Weighting
        # Convert ML class distribution into an ordinal probability score (0-100)
        # Critical=100, High=75, Medium=45, Low=15
        ml_prob_score = (
            (ml_probs.get("Critical", 0.0) * 100.0)
            + (ml_probs.get("High", 0.0) * 75.0)
            + (ml_probs.get("Medium", 0.0) * 45.0)
            + (ml_probs.get("Low", 0.0) * 15.0)
        )

        weights = DEFAULT_WEIGHTS
        raw_urgency_score = (
            (ml_prob_score * weights.ml_weight)
            + (temporal_score * weights.temporal_weight)
            + (business_impact_score * weights.business_weight)
            + (urgency_lang_score * weights.urgency_lang_weight)
            + (context_severity_score * weights.context_severity_weight)
            + sender_bonus
        )

        # Step 8: Cognitive Edge-Case Reasoning & Contextual Modulation
        reasons: List[str] = []

        # Nuance Case A: Marketing / Newsletter / Low-intent false positive suppression
        is_informational_or_promo = (
            intent_label in ["Information", "General Communication"]
            and any(w in combined_text.lower() for w in ["newsletter", "clearance", "discount", "social", "perks", "cafeteria"])
        )
        if is_informational_or_promo:
            if raw_urgency_score > 35.0:
                raw_urgency_score = min(raw_urgency_score, 25.0)
                reasons.append("Urgency buzzwords recognized as marketing/promotional hype; priority suppressed to Low.")

        # Nuance Case B: Severe operational impact without explicit 'urgent' keyword
        has_critical_infra = (
            business_impact_level == "Critical"
            and any(w in combined_text.lower() for w in ["down", "unreachable", "crash", "stopped", "502", "500", "severed", "leaked", "breach"])
        )
        if has_critical_infra:
            raw_urgency_score = max(raw_urgency_score, 85.0)
            reasons.append("Severe operational infrastructure degradation detected regardless of keyword phrasing.")

        # Nuance Case C: Immediate deadline (< 1 hour) with client/production context
        if temporal_score >= 90.0 and business_impact_score >= 70.0:
            raw_urgency_score = max(raw_urgency_score, 88.0)
            reasons.append(f"Critical time constraint ({temporal_constraint}) combined with high business impact.")

        final_urgency_score = int(round(max(0.0, min(100.0, raw_urgency_score))))

        # Map to Urgency Level
        if final_urgency_score >= 76:
            urgency_level = "Critical"
        elif final_urgency_score >= 51:
            urgency_level = "High"
        elif final_urgency_score >= 26:
            urgency_level = "Medium"
        else:
            urgency_level = "Low"

        is_urgent = urgency_level in ["Critical", "High"]
        requires_immediate_attention = (
            urgency_level == "Critical"
            or (urgency_level == "High" and temporal_score >= 70.0)
        )

        # Generate Human-Explainable Reasoning Points
        if business_impact_level in ["Critical", "High"]:
            reasons.append(f"Business & operational impact evaluated as {business_impact_level} (impact: {', '.join(business_result['matched_impacts'][:3])}).")

        if temporal_constraint:
            reasons.append(f"Explicit temporal constraint identified: '{temporal_constraint}'.")

        if urgency_result["critical_matches"]:
            reasons.append(f"Explicit crisis/urgency terms detected: {', '.join(urgency_result['critical_matches'][:3])}.")

        if role_notes:
            reasons.extend(role_notes)

        reasons.append(f"ML probability distribution: Critical={ml_probs.get('Critical', 0.0):.1%}, High={ml_probs.get('High', 0.0):.1%}, Medium={ml_probs.get('Medium', 0.0):.1%}, Low={ml_probs.get('Low', 0.0):.1%}.")

        # Generate Natural Language Explanation
        detailed_explanation = self._build_natural_explanation(
            urgency_level=urgency_level,
            urgency_score=final_urgency_score,
            intent=intent_label,
            temporal_constraint=temporal_constraint,
            business_impact_level=business_impact_level,
            reasons=reasons
        )

        # Recommended Action
        recommended_action = self._determine_recommended_action(
            urgency_level=urgency_level,
            intent=intent_label,
            temporal_constraint=temporal_constraint,
            business_impact=business_impact_level
        )

        # Extract Key Influential Phrases
        important_phrases = self._extract_key_phrases(
            subject=subject,
            body=body,
            temporal_result=temporal_result,
            urgency_result=urgency_result,
            business_result=business_result,
            ml_features=ml_result["top_features"]
        )

        # Generate Highlighted HTML and Spans for UI
        highlighted_html, highlighted_spans = self._generate_highlights(
            subject=subject,
            body=body,
            temporal_result=temporal_result,
            urgency_result=urgency_result,
            business_result=business_result,
            intent_keywords=intent_keywords
        )

        overall_confidence = round(
            (ml_result["confidence"] * 0.6) + (min(1.0, max(temporal_score, business_impact_score) / 100.0) * 0.4),
            2
        )

        return {
            "urgency_level": urgency_level,
            "is_urgent": is_urgent,
            "urgency_score": final_urgency_score,
            "confidence": min(0.99, max(0.65, overall_confidence)),
            "intent": intent_label,
            "intent_confidence": intent_conf,
            "important_phrases": important_phrases,
            "temporal_constraint": temporal_constraint,
            "business_impact": business_impact_level,
            "requires_immediate_attention": requires_immediate_attention,
            "recommended_action": recommended_action,
            "reasoning": reasons,
            "detailed_explanation": detailed_explanation,
            "cognitive_breakdown": {
                "ml_prediction": round(ml_prob_score, 1),
                "temporal_urgency": round(temporal_score, 1),
                "business_impact": round(business_impact_score, 1),
                "urgency_language": round(urgency_lang_score, 1),
                "context_severity": round(context_severity_score, 1)
            },
            "highlighted_html": highlighted_html,
            "highlighted_spans": highlighted_spans,
            "ml_probabilities": ml_probs
        }

    def _determine_recommended_action(
        self,
        urgency_level: str,
        intent: str,
        temporal_constraint: Optional[str],
        business_impact: str
    ) -> str:
        """Prescribe actionable next steps based on urgency and intent context."""
        if urgency_level == "Critical":
            if intent == "Security Alert":
                return "Immediately isolate affected systems, rotate credentials, and notify the Security Incident Response Team."
            elif intent == "Payment Issue":
                return "Initiate emergency payment gateway diagnostics and escalate to finance & infrastructure leads immediately."
            elif intent == "Technical Issue":
                return "Respond immediately, initiate emergency incident bridge, and alert SRE/infrastructure on-call engineers."
            else:
                return "Acknowledge receipt immediately and escalate to senior leadership for immediate intervention."

        elif urgency_level == "High":
            if intent == "Meeting":
                return "Review updated agenda and slides today; confirm calendar availability within 2 hours."
            elif intent == "Deadline":
                return f"Prioritize completion today to satisfy deadline requirement ({temporal_constraint or 'scheduled today'})."
            elif intent == "Job/Interview":
                return "Review candidate profile and confirm panel interview availability today."
            else:
                return "Review this email as soon as possible and send a comprehensive response today."

        elif urgency_level == "Medium":
            if intent == "Request":
                return "Add this request to your active sprint/task queue and respond within 1-2 business days."
            elif intent == "Meeting":
                return "Check calendar schedule and propose alternative meeting slots when convenient."
            else:
                return "Review when convenient and reply during normal working hours."

        else: # Low
            if intent == "Information":
                return "No immediate response needed. File or archive for informational reference."
            else:
                return "No immediate action required. Read at your leisure."

    def _build_natural_explanation(
        self,
        urgency_level: str,
        urgency_score: int,
        intent: str,
        temporal_constraint: Optional[str],
        business_impact_level: str,
        reasons: List[str]
    ) -> str:
        """Compose a coherent human-readable narrative explaining the reasoning."""
        narrative = f"This email has been triaged as **{urgency_level} Priority** with an overall Urgency Score of **{urgency_score}/100**. "
        narrative += f"The cognitive intent was recognized as **{intent}**. "

        if business_impact_level in ["Critical", "High"]:
            narrative += f"The operational context indicates **{business_impact_level} business impact**, threatening customer experience or service continuity. "

        if temporal_constraint:
            narrative += f"The presence of time constraint ('{temporal_constraint}') introduces significant scheduling pressure. "

        narrative += "The decision reflects a balanced synthesis of ML statistical probability, temporal deadline urgency, and domain severity."
        return narrative

    def _extract_key_phrases(
        self,
        subject: str,
        body: str,
        temporal_result: Dict,
        urgency_result: Dict,
        business_result: Dict,
        ml_features: List[Dict]
    ) -> List[str]:
        """Aggregate key influential phrases across all cognitive modalities."""
        phrases = []

        for p in temporal_result.get("matched_expressions", []):
            if p not in phrases:
                phrases.append(p)

        for p in urgency_result.get("critical_matches", []) + urgency_result.get("high_matches", []):
            if p not in phrases:
                phrases.append(p)

        for p in business_result.get("matched_impacts", []):
            if p not in phrases:
                phrases.append(p)

        for item in ml_features[:4]:
            w = item["word"]
            if w not in phrases and len(w) > 3:
                phrases.append(w)

        return phrases[:8]

    def _generate_highlights(
        self,
        subject: str,
        body: str,
        temporal_result: Dict,
        urgency_result: Dict,
        business_result: Dict,
        intent_keywords: List[str]
    ) -> Tuple[str, List[Dict]]:
        """Produce structured highlights and escaped HTML with inline color classes."""
        spans: List[Dict] = []

        # Collect critical phrases
        for p in urgency_result.get("critical_matches", []):
            spans.append({"text": p, "category": "critical", "reason": "Urgency & crisis signal"})

        # Collect temporal phrases
        for p in temporal_result.get("matched_expressions", []):
            spans.append({"text": p, "category": "temporal", "reason": "Deadline or time constraint"})

        # Collect business phrases
        for p in business_result.get("matched_impacts", []):
            spans.append({"text": p, "category": "business", "reason": "Business / operational impact"})

        # Collect intent phrases
        for p in intent_keywords:
            spans.append({"text": p, "category": "intent", "reason": "Intent indicator"})

        # Build highlighted HTML from raw text
        full_text = f"Subject: {subject}\n\n{body}"
        safe_html = html.escape(full_text)

        # Sort spans by length descending so longer phrases match first
        sorted_spans = sorted(spans, key=lambda s: len(s["text"]), reverse=True)
        replaced_tokens = set()

        for s in sorted_spans:
            raw_target = s["text"].strip()
            if not raw_target or raw_target.lower() in replaced_tokens:
                continue

            escaped_target = html.escape(raw_target)
            cat_cls = f"hl-{s['category']}"
            pattern = re.compile(re.escape(escaped_target), re.IGNORECASE)

            safe_html = pattern.sub(
                f'<span class="{cat_cls}" title="{html.escape(s["reason"])}">\\g<0></span>',
                safe_html,
                count=3
            )
            replaced_tokens.add(raw_target.lower())

        # Convert line breaks to <br> for HTML rendering
        html_formatted = safe_html.replace("\n", "<br>")

        return html_formatted, spans

