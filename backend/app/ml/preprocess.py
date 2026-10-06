"""Text preprocessing and NLP feature extraction utilities."""

import re
import string
from typing import Dict, List, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Attempt to load NLTK stopwords safely
try:
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words("english"))
except Exception:
    try:
        nltk.download("stopwords", quiet=True)
        from nltk.corpus import stopwords
        STOPWORDS = set(stopwords.words("english"))
    except Exception:
        STOPWORDS = set()

    # Safe fallback stopwords list if offline
    STOPWORDS = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
        "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
        "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
        "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
        "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
        "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
        "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
        "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll",
        "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's",
        "which", "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't",
        "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves"
    }

# Retain certain urgency-carrying negations or markers
EXCLUDED_FROM_STOPWORDS = {"not", "no", "down", "off", "before", "until", "against", "very"}
CLEAN_STOPWORDS = STOPWORDS - EXCLUDED_FROM_STOPWORDS

try:
    LEMMATIZER = WordNetLemmatizer()
    LEMMATIZER.lemmatize("testing")
except Exception:
    LEMMATIZER = None



def clean_text(text: str, remove_stopwords: bool = True) -> str:
    """Clean text by lowering, removing urls, stripping excess punctuation and stopwords."""
    if not text or not isinstance(text, str):
        return ""

    # Remove URLs and email addresses
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip().lower()

    # Split into words while keeping alphanumeric and basic symbols
    words = re.findall(r"\b[a-z0-9_-]+\b", text)

    if remove_stopwords:
        words = [w for w in words if w not in CLEAN_STOPWORDS]

    if LEMMATIZER:
        try:
            words = [LEMMATIZER.lemmatize(w) for w in words]
        except Exception:
            pass

    return " ".join(words)


def extract_structural_features(subject: str, body: str) -> Dict[str, float]:
    """Extract surface linguistic and typographical signals of urgency.
    
    Cognitive rationale: Human perception of urgency in written communication
    is heavily mediated by typographical emphasis (ALL CAPS, multiple exclamation
    marks, short imperative structure).
    """
    combined = f"{subject} {body}"
    words = re.findall(r"\b[A-Za-z0-9]+\b", combined)
    total_words = len(words) if words else 1

    # Count exclamation marks and question marks
    exclamation_count = combined.count("!")
    question_count = combined.count("?")

    # Calculate uppercase ratio among alphabetic characters
    alpha_chars = [c for c in combined if c.isalpha()]
    upper_chars = [c for c in alpha_chars if c.isupper()]
    upper_ratio = len(upper_chars) / len(alpha_chars) if alpha_chars else 0.0

    # Check for consecutive exclamation marks (e.g., "!!!" or "?!")
    urgent_punct_patterns = len(re.findall(r"!{2,}|\?!|!\?", combined))

    # Subject urgency marker: does subject start with or contain tags like [URGENT]
    subject_has_alert_tag = bool(re.search(r"\[?(urgent|critical|action required|emergency|asap|alert)\]?", subject, re.IGNORECASE))

    return {
        "word_count": float(total_words),
        "exclamation_count": float(exclamation_count),
        "question_count": float(question_count),
        "upper_ratio": float(round(upper_ratio, 3)),
        "urgent_punct_patterns": float(urgent_punct_patterns),
        "subject_has_alert_tag": 1.0 if subject_has_alert_tag else 0.0,
    }


def prepare_combined_text(subject: str, body: str, repeat_subject: int = 2) -> str:
    """Concatenate subject and body with subject weighting.
    
    In cognitive email reading, subject lines receive higher perceptual priority
    from human readers, so we repeat the subject to naturally reflect its weight.
    """
    clean_sub = (subject or "").strip()
    clean_bod = (body or "").strip()
    weighted_subject = " ".join([clean_sub] * repeat_subject)
    return f"{weighted_subject} {clean_bod}".strip()

