#!/usr/bin/env python3
"""
Disaster & Space Events Domain for Nostradamus Analysis
Extracts disaster and celestial event signals from quatrains,
maps them to real-world catalogs (EM-DAT, NASA NEO, NOAA Space Weather).

Nostradamus's symbolic vocabulary overlaps with these domains:
- "earth shaking", "land sliding" → earthquake
- "fire from heaven", "flames in the sky" → solar storm / wildfire
- "great flood", "waters rising" → flood / tsunami
- "two suns", "blood-red moon" → celestial / eclipse
- "star falling", "stone from the sky" → asteroid
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import re
import html

# === KEYWORD DICTIONARIES ===

# Middle French / archaic French keywords for disaster types
# Sorted by specificity; longer/more specific phrases first
DISASTER_KEYWORDS: Dict[str, List[str]] = {
    "earthquake": [
        "terre trembler",
        "tremblement de terre",
        "terremotus",
        "secousse",
        "la terre movra",
        "la terre s esmouvra",
        "la terre fendu",
        "terre fendu",
        "montagne crouler",
        "rochers cheoir",
    ],
    "tsunami": [
        "vague grand",
        "mer monter",
        "inondation marin",
        "eaux marin",
        "flots enorme",
        "mariner Mons",
    ],
    "volcanic": [
        "feu grond",
        "volcan",
        "montagne flamber",
        "lave couler",
        "ember z",
        "braz",
        "cendre volcan",
        "magma",
    ],
    "wildfire": [
        "forest brusler",
        "forest incend",
        "flamber",
        "feu grand",
        "incend",
        "braslar",
        "ciel en feu",
    ],
    "drought": [
        "secheresse",
        "chaleur grand",
        "eaux manque",
        "siccite",
        "aridite",
        "sans pluye",
        "pluye non",
        "fontaine secher",
    ],
    "flood": [
        "dilinvee",
        "inondation",
        "deluge",
        "eaux monter",
        "pluye grand",
        "eaux desbord",
        "fleuve deborder",
    ],
}

# Celestial / space event keywords
SPACE_KEYWORDS: Dict[str, List[str]] = {
    "solar_storm": [
        "aurore",
        "aurora",
        "flammes ciel",
        "coron",
        "masse solaire",
        "vent solaire",
        "feu du ciel",
        "lumiere celest",
    ],
    "asteroid": [
        "astre cheoir",
        "pierre ciel",
        "asteroid",
        "meteor",
        "meteorite",
        "pierre cheoir",
        "chute astre",
    ],
    "comet": [
        "comete",
        "trouble estoille",
        "estoille queue",
        "queue estoille",
        "chevelure estoille",
        "astre queue",
        "etoile trenchant",
    ],
    "eclipse": [
        "eclipse",
        "soleil obscur",
        "lune obscur",
        "obscurcissement",
        "tenebres",
        "soleil noir",
        "lune sang",
        "tenebres grand",
    ],
    "aurora": [
        "aurore",
        "aurora borealis",
        "lueur polaire",
        "ciel roug",
        "ciel en feu",
    ],
}

# === INTENSITY SCALES ===

DISASTER_INTENSITY: Dict[str, Dict[str, Tuple[float, float]]] = {
    "earthquake": {"major": (7.0, 10.0), "severe": (5.5, 7.0), "moderate": (4.0, 5.5)},
    "wildfire": {"major": (10000, 100000), "severe": (1000, 10000), "moderate": (100, 1000)},  # hectares
    "flood": {"major": (1000000, 10000000), "severe": (100000, 1000000), "moderate": (10000, 100000)},  # people affected
    "drought": {"major": (36, 60), "severe": (12, 36), "moderate": (6, 12)},  # months
}

# === LOCATION HINTS ===

DISASTER_REGION_HINTS: Dict[str, List[str]] = {
    "Pacific_Rim": ["japon", "chine", "inde", "indonesie", "pacific", "pacifique",
                     "tokyo", "osaka", "djakarta", "manille", "auckland"],
    "Mediterranean": ["grece", "italie", "espagne", "turc", "portugal",
                      "athenes", "rome", "lisbonne", "constantin"],
    "Global": ["monde", "global", "univers", "toute la terre"],
    "Europe": ["france", "angleterre", "allemagne", "europe"],
}


# === PROFILE DATACLASSES ===

@dataclass
class DisasterProfile:
    """Profile for a quatrain's disaster event signals."""
    quatrain_id: str
    detected_types: List[str] = field(default_factory=list)
    intensity_estimate: str = "unknown"  # moderate / severe / major
    location_hints: List[str] = field(default_factory=list)
    temporal_markers: List[str] = field(default_factory=list)
    confidence: float = 0.0
    matching_keywords: Dict[str, List[str]] = field(default_factory=dict)
    extraction_notes: List[str] = field(default_factory=list)


@dataclass
class SpaceProfile:
    """Profile for a quatrain's celestial / space event signals."""
    quatrain_id: str
    detected_types: List[str] = field(default_factory=list)
    celestial_coordinates_approx: Optional[str] = None
    temporal_markers: List[str] = field(default_factory=list)
    real_event_matches: List[Dict] = field(default_factory=list)
    confidence: float = 0.0
    matching_keywords: Dict[str, List[str]] = field(default_factory=dict)
    extraction_notes: List[str] = field(default_factory=list)


# === ANALYSIS FUNCTIONS ===

def analyze_disaster(text: str, quatrain_id: str) -> DisasterProfile:
    """
    Analyze a quatrain's text for natural disaster signals.

    Returns a DisasterProfile with detected types, location hints, and confidence.
    """
    # Decode HTML entities (e.g., &amp; → &, &lt; → <)
    text_clean = html.unescape(text)
    text_lower = text_clean.lower()
    profile = DisasterProfile(quatrain_id=quatrain_id)
    type_scores: Dict[str, float] = {}

    for disaster_type, keywords in DISASTER_KEYWORDS.items():
        matched = []
        for kw in keywords:
            if kw in text_lower:
                matched.append(kw)
        if matched:
            type_scores[disaster_type] = len(matched)
            profile.matching_keywords[disaster_type] = matched

    if not type_scores:
        profile.extraction_notes.append("no disaster keywords detected")
        return profile

    # Determine dominant type (highest keyword count)
    profile.detected_types = sorted(type_scores.keys(), key=lambda t: -type_scores[t])

    # Estimate intensity from keyword density
    total_matches = sum(type_scores.values())
    if total_matches >= 4:
        profile.intensity_estimate = "major"
        profile.confidence = min(0.9, 0.5 + total_matches * 0.1)
    elif total_matches >= 2:
        profile.intensity_estimate = "severe"
        profile.confidence = min(0.7, 0.4 + total_matches * 0.1)
    else:
        profile.intensity_estimate = "moderate"
        profile.confidence = min(0.5, 0.3 + total_matches * 0.15)

    # Extract location hints
    for region, hints in DISASTER_REGION_HINTS.items():
        for hint in hints:
            if hint in text_lower:
                profile.location_hints.append(region)
                break

    # Extract temporal markers
    profile.temporal_markers = _extract_temporal_markers(text_lower)

    return profile


def analyze_space(text: str, quatrain_id: str) -> SpaceProfile:
    """
    Analyze a quatrain's text for celestial / space event signals.

    Returns a SpaceProfile with detected types and potential real-event matches.
    """
    # Decode HTML entities (e.g., &amp; → &, &lt; → <)
    text_clean = html.unescape(text)
    text_lower = text_clean.lower()
    profile = SpaceProfile(quatrain_id=quatrain_id)
    type_scores: Dict[str, float] = {}

    for space_type, keywords in SPACE_KEYWORDS.items():
        matched = []
        for kw in keywords:
            if kw in text_lower:
                matched.append(kw)
        if matched:
            type_scores[space_type] = len(matched)
            profile.matching_keywords[space_type] = matched

    if not type_scores:
        profile.extraction_notes.append("no space/celestial keywords detected")
        return profile

    profile.detected_types = sorted(type_scores.keys(), key=lambda t: -type_scores[t])

    # Confidence based on keyword density
    total_matches = sum(type_scores.values())
    if total_matches >= 3:
        profile.confidence = min(0.85, 0.4 + total_matches * 0.15)
    elif total_matches >= 1:
        profile.confidence = min(0.6, 0.3 + total_matches * 0.2)

    # Extract temporal markers
    profile.temporal_markers = _extract_temporal_markers(text_lower)

    return profile


def analyze_disaster_space(text: str, quatrain_id: str) -> Dict:
    """
    Combined analysis for both disaster and space events.

    Returns a dict with 'disaster' and 'space' sub-profiles,
    suitable for inclusion in the full quatrain analysis pipeline.
    """
    disaster_profile = analyze_disaster(text, quatrain_id)
    space_profile = analyze_space(text, quatrain_id)

    return {
        "quatrain_id": quatrain_id,
        "disaster": {
            "detected_types": disaster_profile.detected_types,
            "intensity_estimate": disaster_profile.intensity_estimate,
            "location_hints": disaster_profile.location_hints,
            "temporal_markers": disaster_profile.temporal_markers,
            "confidence": round(disaster_profile.confidence, 3),
            "matching_keywords": disaster_profile.matching_keywords,
        },
        "space": {
            "detected_types": space_profile.detected_types,
            "temporal_markers": space_profile.temporal_markers,
            "confidence": round(space_profile.confidence, 3),
            "matching_keywords": space_profile.matching_keywords,
        },
        "has_disaster_signal": len(disaster_profile.detected_types) > 0,
        "has_space_signal": len(space_profile.detected_types) > 0,
        "dominant_signal": (
            "disaster" if disaster_profile.confidence > space_profile.confidence
            else "space" if space_profile.confidence > 0
            else "none"
        ),
    }


def _extract_temporal_markers(text_lower: str) -> List[str]:
    """Extract temporal markers from text (years, seasons, phrases)."""
    markers = []

    # Year patterns
    year_patterns = re.findall(r'\b(1[0-9]{3}|20[0-2][0-9])\b', text_lower)
    markers.extend([f"year:{y}" for y in year_patterns])

    # Seasonal/weather markers
    season_words = {
        "printemps": "spring", "este": "summer", "automne": "autumn",
        "hyver": "winter", "hiver": "winter",
        "janvier": "january", "mars": "march", "may": "may",
        "juin": "june", "juillet": "july", "aoust": "august",
    }
    for fr, en in season_words.items():
        if fr in text_lower:
            markers.append(f"season:{en}")

    # Relative time phrases
    relative = {
        "bientot": "soon", "tantost": "soon", "promptement": "soon",
        "longtemps": "long", "annees": "years", "siecle": "century",
        "aultant": "equal", "apres": "after", "devant": "before",
    }
    for fr, en in relative.items():
        if fr in text_lower:
            markers.append(f"time:{en}")

    return list(set(markers))


def get_catalog_stats() -> Dict:
    """
    Return summary statistics from the disasters_space_kb.
    Used to compute pattern significance against real event frequencies.
    """
    try:
        from nostradamus.data.disasters_space_kb import DISASTERS_KB, SPACE_EVENTS_KB

        disaster_types = {}
        for e in DISASTERS_KB:
            t = e.get("event_type", "unknown")
            disaster_types[t] = disaster_types.get(t, 0) + 1

        space_types = {}
        for e in SPACE_EVENTS_KB:
            t = e.get("event_type", "unknown")
            space_types[t] = space_types.get(t, 0) + 1

        return {
            "total_disaster_events": len(DISASTERS_KB),
            "total_space_events": len(SPACE_EVENTS_KB),
            "disaster_types": disaster_types,
            "space_types": space_types,
            "disaster_frequency_per_year": round(len(DISASTERS_KB) / 500, 1),  # ~500 years of data
            "space_frequency_per_year": round(len(SPACE_EVENTS_KB) / 500, 1),
        }
    except ImportError:
        return {"error": "disasters_space_kb not available"}


# === MONTE CARLO VALIDATION HELPERS ===

def disaster_significance(observed_count: int, expected_rate: float, years: int) -> float:
    """
    Compute approximate p-value for disaster event frequency.

    Uses Poisson approximation: P(X >= observed) given lambda = expected_rate * years
    """
    import math
    if observed_count == 0:
        return 1.0
    try:
        from scipy.stats import poisson
        lambda_ = expected_rate * years
        p_value = 1 - poisson.cdf(observed_count - 1, lambda_)
        return round(p_value, 4)
    except ImportError:
        # Fallback: rough approximation
        return 0.5
