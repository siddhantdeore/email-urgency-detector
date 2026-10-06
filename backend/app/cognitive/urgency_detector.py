"""Cognitive Urgency Signal & Business Impact Detector.

Extracts explicit urgency lexicon, operational alarm signals,
and business impact severity.
"""

import re
from typing import Dict, List, Tuple


# Lexicon Categories
CRITICAL_SIGNALS = [
    r"\burgent\b", r"\bcritical\b", r"\bemergency\b", r"\bserver is down\b",
    r"\bdown\b", r"\boffline\b", r"\boutage\b", r"\bcatastrophic\b",
    r"\bsecurity breach\b", r"\bdata breach\b", r"\bransomware\b", r"\bcompromised\b",
    r"\bfailure\b", r"\bfailed\b", r"\bfailover\b", r"\bunresponsive\b",
    r"\bp1\b", r"\bsev-?1\b", r"\bcrashloop\b", r"\bcatastrophic\b",
    r"\baction required\b", r"\bimmediate attention\b", r"\bresolve immediately\b",
    r"\brisk of data loss\b", r"\broot key leak\b", r"\bmalicious\b"
]

HIGH_SIGNALS = [
    r"\bimportant\b", r"\bdeadline\b", r"\bhigh priority\b", r"\bescalat(?:ed|ion)\b",
    r"\bblocker\b", r"\bat risk\b", r"\bexpedite\b", r"\boverdue\b",
    r"\bnon-compliance\b", r"\bdisruption\b", r"\blapse\b", r"\bhotfix\b"
]

BUSINESS_IMPACT_CATEGORIES = {
    "Critical": [
        r"\bproduction\b", r"\bcore database\b", r"\bpayment gateway\b", r"\bcheckout\b",
        r"\brevenue loss\b", r"\bactive customer transactions\b", r"\bsla breach\b",
        r"\bhospital\b", r"\bpatient monitoring\b", r"\blegal hold\b", r"\bsec compliance\b",
        r"\benterprise client\b", r"\bclient demonstration\b", r"\bboard meeting\b"
    ],
    "High": [
        r"\bclient\b", r"\bcustomer\b", r"\bvendor\b", r"\bcontract\b", r"\baudit\b",
        r"\btax filing\b", r"\bpayroll\b", r"\bquarterly\b", r"\bexecutive\b",
        r"\binterview\b", r"\bthesis\b", r"\bpress release\b"
    ],
    "Medium": [
        r"\bproject\b", r"\bproposal\b", r"\bmockup\b", r"\bwireframe\b",
        r"\bdesign\b", r"\bsprint\b", r"\bexpense\b", r"\bconcur\b",
        r"\barchitecture\b", r"\breview\b", r"\bdocumentation\b"
    ],
    "Low": [
        r"\bnewsletter\b", r"\bbook club\b", r"\bcoffee\b", r"\blounge\b",
        r"\blunch\b", r"\bwebinar\b", r"\bdiscount\b", r"\bstationery\b",
        r"\bperks\b", r"\btaco\b", r"\bpicnic\b", r"\bphotos\b"
    ]
}


class UrgencySignalDetector:
    """Detects urgency signals, business impact, and typographical distress."""

    def analyze_urgency_signals(self, text: str) -> Dict[str, any]:
        """Assess explicit urgency terminology and emotional intensity."""
        if not text:
            return {
                "urgency_language_score": 0.0,
                "critical_matches": [],
                "high_matches": [],
                "context_severity_score": 0.0,
            }

        text_lower = text.lower()

        # Find critical matches
        crit_matches = []
        for pat in CRITICAL_SIGNALS:
            m = re.findall(pat, text_lower)
            if m:
                crit_matches.extend(m)

        # Find high matches
        high_matches = []
        for pat in HIGH_SIGNALS:
            m = re.findall(pat, text_lower)
            if m:
                high_matches.extend(m)

        # Calculate Urgency Language score
        lang_score = 0.0
        if crit_matches:
            lang_score = min(100.0, 60.0 + (len(crit_matches) * 15.0))
        elif high_matches:
            lang_score = min(85.0, 40.0 + (len(high_matches) * 12.0))
        else:
            lang_score = 10.0

        # Context Severity: evaluate structural intensity (exclamations, ALL CAPS, imperative patterns)
        words = text.split()
        caps_words = [w for w in words if len(w) > 2 and w.isupper() and w.isalpha()]
        exclamation_count = text.count("!")
        consecutive_punct = len(re.findall(r"!{2,}|\?!", text))

        severity_score = 0.0
        if len(caps_words) >= 3 or consecutive_punct >= 1 or exclamation_count >= 3:
            severity_score = min(95.0, 50.0 + (len(caps_words) * 10.0) + (exclamation_count * 8.0))
        elif len(caps_words) >= 1 or exclamation_count >= 1:
            severity_score = 45.0
        else:
            severity_score = 15.0

        return {
            "urgency_language_score": round(lang_score, 1),
            "critical_matches": list(set(crit_matches)),
            "high_matches": list(set(high_matches)),
            "context_severity_score": round(severity_score, 1),
            "uppercase_words": caps_words[:5],
            "exclamation_count": exclamation_count
        }

    def analyze_business_impact(self, text: str) -> Dict[str, any]:
        """Determine business criticality and domain impact."""
        if not text:
            return {
                "impact_level": "None",
                "impact_score": 0.0,
                "matched_impacts": []
            }

        text_lower = text.lower()
        matched = []

        for crit_pat in BUSINESS_IMPACT_CATEGORIES["Critical"]:
            if re.search(crit_pat, text_lower):
                matched.append(crit_pat.replace(r"\b", ""))
        if matched:
            return {
                "impact_level": "Critical",
                "impact_score": 95.0,
                "matched_impacts": matched
            }

        for high_pat in BUSINESS_IMPACT_CATEGORIES["High"]:
            if re.search(high_pat, text_lower):
                matched.append(high_pat.replace(r"\b", ""))
        if matched:
            return {
                "impact_level": "High",
                "impact_score": 75.0,
                "matched_impacts": matched
            }

        for med_pat in BUSINESS_IMPACT_CATEGORIES["Medium"]:
            if re.search(med_pat, text_lower):
                matched.append(med_pat.replace(r"\b", ""))
        if matched:
            return {
                "impact_level": "Medium",
                "impact_score": 45.0,
                "matched_impacts": matched
            }

        for low_pat in BUSINESS_IMPACT_CATEGORIES["Low"]:
            if re.search(low_pat, text_lower):
                matched.append(low_pat.replace(r"\b", ""))
        if matched:
            return {
                "impact_level": "Low",
                "impact_score": 15.0,
                "matched_impacts": matched
            }

        return {
            "impact_level": "None",
            "impact_score": 10.0,
            "matched_impacts": []
        }

