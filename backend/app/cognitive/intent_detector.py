"""Cognitive Intent Detector.

Fuses ML intent classification with cognitive domain patterns.
"""

import re
from typing import Dict, List, Tuple

INTENT_RULES = {
    "Security Alert": [
        r"\bsecurity\b", r"\bbreach\b", r"\bransomware\b", r"\bmalicious\b",
        r"\bunauthorized\b", r"\bcredential\b", r"\bssh key\b", r"\bhack(?:ed)?\b",
        r"\bvulnerability\b", r"\bcve\b", r"\bfirewall\b", r"\bphishing\b"
    ],
    "Payment Issue": [
        r"\bpayment\b", r"\bcheckout\b", r"\bstripe\b", r"\bpaypal\b",
        r"\binvoice\b", r"\bbilling\b", r"\btransaction\b", r"\bpayroll\b",
        r"\bach\b", r"\bdirect deposit\b", r"\brevenue loss\b"
    ],
    "Technical Issue": [
        r"\bserver\b", r"\bdatabase\b", r"\bcrash\b", r"\b502\b", r"\b500\b",
        r"\bpostgres\b", r"\bkubernetes\b", r"\bingress\b", r"\boutage\b",
        r"\bcluster\b", r"\bcache\b", r"\bmemory exhausted\b", r"\bapi\b", r"\bhotfix\b"
    ],
    "Job/Interview": [
        r"\binterview\b", r"\bcandidate\b", r"\boffer letter\b", r"\bhiring\b",
        r"\brecruiter\b", r"\bgreenhouse\b", r"\bscorecard\b", r"\bresume\b"
    ],
    "Academic": [
        r"\bthesis\b", r"\bprofessor\b", r"\bstudent\b", r"\bhomework\b",
        r"\bdefense\b", r"\badvisory committee\b", r"\boffice hours\b", r"\bexam\b"
    ],
    "Meeting": [
        r"\bmeeting\b", r"\bsync\b", r"\bcalendar\b", r"\b1-on-1\b",
        r"\breschedul(?:e|ed|ing)\b", r"\bcall\b", r"\bconference\b"
    ],
    "Complaint": [
        r"\bdissatisfaction\b", r"\bunacceptable\b", r"\bcomplaint\b",
        r"\bescalated\b", r"\bunhappy\b", r"\bfailed expectations\b"
    ],
    "Deadline": [
        r"\bdeadline\b", r"\bdue date\b", r"\btax filing\b", r"\bpress release\b",
        r"\bcutoff\b", r"\blegal hold\b", r"\baudit\b"
    ],
    "Request": [
        r"\bplease review\b", r"\bcan you\b", r"\bcould you\b", r"\bapproval needed\b",
        r"\bkindly\b", r"\brequest\b", r"\bsign-off\b", r"\bfeedback\b"
    ],
    "Information": [
        r"\bnewsletter\b", r"\bdigest\b", r"\bwebinar\b", r"\bannouncement\b",
        r"\bsharing\b", r"\bdiscount\b", r"\bmenu\b", r"\bnotes\b", r"\bfor reference\b"
    ]
}


class IntentDetector:
    """Classifies email intent through dual-channel cognitive perception."""

    def detect(self, subject: str, body: str, ml_intent: str, ml_confidence: float) -> Tuple[str, float, List[str]]:
        """Combine ML prediction with semantic cue verification."""
        combined = f"{subject} {body}".lower()
        matched_cues: Dict[str, List[str]] = {}

        for intent_cat, patterns in INTENT_RULES.items():
            hits = []
            for pat in patterns:
                if re.search(pat, combined):
                    hits.append(pat.replace(r"\b", ""))
            if hits:
                matched_cues[intent_cat] = hits

        # High priority semantic override for critical security/payment/infrastructure alerts
        if "Security Alert" in matched_cues and len(matched_cues["Security Alert"]) >= 2:
            return "Security Alert", max(ml_confidence, 0.95), matched_cues["Security Alert"]

        if "Payment Issue" in matched_cues and len(matched_cues["Payment Issue"]) >= 2:
            return "Payment Issue", max(ml_confidence, 0.94), matched_cues["Payment Issue"]

        if "Technical Issue" in matched_cues and len(matched_cues["Technical Issue"]) >= 2:
            return "Technical Issue", max(ml_confidence, 0.93), matched_cues["Technical Issue"]

        # Default to ML model's prediction if confidence is strong
        if ml_confidence >= 0.65:
            keywords = matched_cues.get(ml_intent, [])
            return ml_intent, ml_confidence, keywords

        # If ML is uncertain, check strongest rule category
        if matched_cues:
            best_cat = max(matched_cues.keys(), key=lambda k: len(matched_cues[k]))
            return best_cat, 0.82, matched_cues[best_cat]

        return ml_intent or "General Communication", ml_confidence or 0.70, []

