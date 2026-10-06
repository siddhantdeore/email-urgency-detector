"""Cognitive Temporal Analyzer.

Extracts time constraints, relative and explicit deadlines, and assigns
a calibrated temporal urgency score (0-100).
"""

import re
from typing import Dict, List, Optional, Tuple


# Regex patterns ordered by severity
TEMPORAL_PATTERNS = [
    # Tier 1: Immediate & Sub-hour (< 1 hour, right now)
    (
        r"\b(?:in\s+\d+\s+min(?:ute)?s?|within\s+\d+\s+min(?:ute)?s?|under\s+\d+\s+min(?:ute)?s?|"
        r"within\s+(?:an?|one|\d+)\s+hour|in\s+(?:an?|one)\s+hour|immediately|right\s+now|at\s+once|"
        r"in\s+(?:the\s+)?next\s+\d+\s+min(?:ute)?s?|asap|urgently)\b",
        95.0,
        "Critical"
    ),
    # Tier 2: Same-day deadlines (Today, before X PM, EOD, within 2-4 hours)
    (
        r"\b(?:today|tonight|this\s+afternoon|before\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)|"
        r"by\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)|end\s+of\s+day|eod|cob|close\s+of\s+business|"
        r"within\s+[2-4]\s+hours?|in\s+[2-4]\s+hours?|before\s+noon|by\s+midnight)\b",
        80.0,
        "High"
    ),
    # Tier 3: Next day / 24 hours (Tomorrow, within 24 hours)
    (
        r"\b(?:tomorrow(?:\s+morning|\s+afternoon)?|within\s+24\s+hours?|in\s+24\s+hours?|"
        r"next\s+24\s+hours?|by\s+tomorrow)\b",
        65.0,
        "High"
    ),
    # Tier 4: This week / few days (By Friday, in 2-3 days)
    (
        r"\b(?:this\s+week|by\s+(?:monday|tuesday|wednesday|thursday|friday)|"
        r"within\s+[2-5]\s+days?|in\s+[2-5]\s+days?|before\s+the\s+weekend)\b",
        40.0,
        "Medium"
    ),
    # Tier 5: Low urgency / flexible timing
    (
        r"\b(?:next\s+week|next\s+month|in\s+(?:a\s+few|several)\s+weeks?|"
        r"when\s+you\s+(?:get\s+a\s+chance|have\s+time|can)|when\s+convenient|"
        r"at\s+your\s+convenience|whenever\s+possible|no\s+rush)\b",
        10.0,
        "Low"
    )
]


class TemporalAnalyzer:
    """Cognitive parser for temporal deadlines and urgency constraints."""

    def analyze(self, text: str) -> Dict[str, any]:
        """Parse text for temporal expressions and calculate temporal urgency."""
        if not text:
            return {
                "temporal_score": 0.0,
                "detected_constraint": None,
                "matched_expressions": [],
                "urgency_tier": "None",
                "is_urgent_timeframe": False
            }

        text_lower = text.lower()
        matched_expressions: List[str] = []
        max_score = 0.0
        primary_tier = "None"
        best_match_phrase: Optional[str] = None

        for pattern, score, tier in TEMPORAL_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                for m in matches:
                    matched_str = m.strip()
                    if matched_str not in matched_expressions:
                        matched_expressions.append(matched_str)
                if score > max_score:
                    max_score = score
                    primary_tier = tier
                    best_match_phrase = matches[0].strip()

        # Check for explicit negative modifier (e.g. "no rush", "when you have time")
        if re.search(r"\b(no\s+rush|no\s+hurry|whenever\s+you\s+can|at\s+your\s+leisure)\b", text_lower):
            max_score = min(max_score, 15.0)
            primary_tier = "Low"

        # Explicit timeframe tag
        detected_constraint = best_match_phrase.capitalize() if best_match_phrase else None

        return {
            "temporal_score": round(max_score, 1),
            "detected_constraint": detected_constraint,
            "matched_expressions": matched_expressions,
            "urgency_tier": primary_tier,
            "is_urgent_timeframe": max_score >= 60.0
        }

