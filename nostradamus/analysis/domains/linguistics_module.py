#!/usr/bin/env python3
"""
Linguistics Module for Nostradamus Prophecies
Middle French normalization, ambiguity analysis, tokenization.
"""

import re
from typing import Dict, List

# Archaic Middle French to Modern French mapping
ARCHAIC_TO_MODERN = {
    "estude": "etude", "ault": "autre", "maistre": "maitre",
    "faict": "fait", "pouldres": "poudres", "encores": "encore",
    "aultant": "autant", "aultre": "autre", "biẽ": "bien",
    "grandg": "grand", " lors ": " lors ", " fault ": " faut ",
    " quoy ": " quoi ", "deffunct": "defunt", "mars": "mars",
    "nimbe": "nymphe", "phares": "fares", "sera": "ete",
    "seront": "etes", "ayans": "ayants", "faict": "fait",
    "portugual": "portugal", "hongrie": "hongrie",
    " et ": " et ", " ou ": " ou ", " ne ": " ne ",
    " ly ": " li ", " la ": " la ", " le ": " le ",
}

# French stopwords
FRENCH_STOPWORDS = {
    "le", "la", "les", "un", "une", "des", "du", "de", "au", "aux",
    "et", "ou", "mais", "donc", "car", "ni", "que", "qui", "quoi",
    "ne", "pas", "plus", "moins", "tres", "bien", "mal", "si",
    "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
    "mon", "ton", "son", "notre", "votre", "leur",
    "ce", "cet", "cette", "ces", "celui", "celle", "ceux", "celles",
    "se", "me", "te", "lui", "leur", "nous", "vous",
    "en", "y", "avec", "sans", "pour", "par", "sur", "sous",
    "dans", "hors", "chez", "entre", "avant", "apres", "depuis",
    "quand", "comme", "plus", "autant", "tant", "quel", "quelle",
    "quelque", "tous", "tout", "toute", "meme", "autre",
}

# Non-French indicator words
NON_FRENCH_MARKERS = {
    "the", "and", "of", "to", "in", "is", "it", "that", "this",
    "with", "for", "on", "at", "by", "from", "as", "be", "was",
    "were", "are", "been", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "must",
}


def normalize_middle_french(text: str) -> str:
    """Normalize archaic Middle French to standard modern French."""
    result = text.lower()
    for archaic, modern in ARCHAIC_TO_MODERN.items():
        result = result.replace(archaic, modern)
    # Remove diacritics for comparison (optional)
    result = result.replace("ẽ", "e").replace("õ", "o").replace("ã", "a")
    return result


def tokenize(text: str) -> List[str]:
    """Split text into tokens, keeping important words."""
    # Remove punctuation except apostrophes, then split
    text = re.sub(r"[^\w\s']", " ", text.lower())
    tokens = [t.strip("'") for t in text.split() if len(t.strip("'")) > 1]
    return tokens


def calculate_ambiguity_index(text: str) -> float:
    """
    Calculate ambiguity index for a quatrain.
    Based on: non-French tokens, word length distribution, multi-language ratio.
    Returns 0.0 (clear) to 1.0 (highly ambiguous).
    """
    tokens = tokenize(text)
    if not tokens:
        return 0.5

    non_french_count = sum(1 for t in tokens if t.lower() in NON_FRENCH_MARKERS)
    short_tokens = sum(1 for t in tokens if len(t) <= 3)

    non_french_ratio = non_french_count / len(tokens)
    short_ratio = short_tokens / len(tokens)

    # Calculate entropy-like measure
    word_lengths = [len(t) for t in tokens]
    avg_length = sum(word_lengths) / len(word_lengths)
    length_variance = sum((l - avg_length) ** 2 for l in word_lengths) / len(word_lengths)

    # Normalize to 0-1 range
    ambiguity = min(1.0, (non_french_ratio * 0.4 + short_ratio * 0.3 + length_variance / 100 * 0.3))
    return round(ambiguity, 3)


def detect_language(tokens: List[str]) -> Dict[str, float]:
    """Detect language distribution in tokens."""
    fr_count = sum(1 for t in tokens if t.lower() not in NON_FRENCH_MARKERS)
    non_fr_count = len(tokens) - fr_count

    total = len(tokens)
    return {
        "french_ratio": fr_count / total if total > 0 else 0.0,
        "non_french_ratio": non_fr_count / total if total > 0 else 0.0,
    }


def analyze_text(text_fr: str, text_en: str = None) -> Dict:
    """
    Main linguistics analysis entry point.

    Args:
        text_fr: Original French text (preserved exactly)
        text_en: English translation (optional)

    Returns:
        Dict with: tokens, normalized_text, ambiguity_index,
                   language_distribution, multi_language flag
    """
    tokens = tokenize(text_fr)
    normalized = normalize_middle_french(text_fr)
    ambiguity = calculate_ambiguity_index(text_fr)
    lang_dist = detect_language(tokens)
    multi_lang = lang_dist["non_french_ratio"] > 0.15

    return {
        "tokens": tokens,
        "normalized_text": normalized,
        "ambiguity_index": ambiguity,
        "language_distribution": lang_dist,
        "multi_language": multi_lang,
        "token_count": len(tokens),
        "stopword_ratio": sum(1 for t in tokens if t.lower() in FRENCH_STOPWORDS) / len(tokens) if tokens else 0.0
    }
