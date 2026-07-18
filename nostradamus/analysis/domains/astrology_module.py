#!/usr/bin/env python3
"""
Astrology Module for Nostradamus Prophecies
Judicial astrology, Ptolemaic planetary symbolism, celestial configurations.
"""

import re
from typing import Dict, List

# Planetary symbolism from 16th century judicial astrology
PLANET_SYMBOLISM = {
    "Soleil": {
        "meaning": "kings, monarchs, power, life force",
        "events": ["coronations", "royal deaths", "reigns", "succession"],
        "nature": "hot and dry, diurnal",
        "signs": ["Leo", "Cancer"],
    },
    "Lune": {
        "meaning": "the people, public affairs, flux",
        "events": ["revolutions", "popular uprisings", "changes"],
        "nature": "cold and moist, nocturnal",
        "signs": ["Cancer"],
    },
    "Mars": {
        "meaning": "war, aggression, fire, destruction",
        "events": ["battles", "sieges", "revolutions", "plague"],
        "nature": "hot and dry, diurnal",
        "signs": ["Aries", "Scorpio"],
    },
    "Mercure": {
        "meaning": "communication, intellect, travel, commerce",
        "events": ["treaties", "letters", "messages", "trade"],
        "nature": "neutral, both",
        "signs": ["Gemini", "Virgo"],
    },
    "Jupiter": {
        "meaning": "kingship, expansion, religion, law",
        "events": ["coronations", "treaties", "religious events", "peace"],
        "nature": "hot and moist, diurnal",
        "signs": ["Sagittarius", "Pisces"],
    },
    "Venus": {
        "meaning": "love, beauty, harmony, fertility",
        "events": ["marriages", "alliances", "celebrations", "abundance"],
        "nature": "cold and moist, nocturnal",
        "signs": ["Taurus", "Libra"],
    },
    "Saturn": {
        "meaning": "time, death, limitation, tradition",
        "events": ["plague", "famine", "death of kings", "structural change"],
        "nature": "cold and dry, diurnal",
        "signs": ["Capricorn", "Aquarius"],
    },
}

# Zodiac signs
ZODIAC_SIGNS = {
    "Aries": {"element": "fire", "planet": "Mars"},
    "Taurus": {"element": "earth", "planet": "Venus"},
    "Gemini": {"element": "air", "planet": "Mercure"},
    "Cancer": {"element": "water", "planet": "Lune"},
    "Leo": {"element": "fire", "planet": "Soleil"},
    "Virgo": {"element": "earth", "planet": "Mercure"},
    "Libra": {"element": "air", "planet": "Venus"},
    "Scorpio": {"element": "water", "planet": "Mars"},
    "Sagittarius": {"element": "fire", "planet": "Jupiter"},
    "Capricorn": {"element": "earth", "planet": "Saturn"},
    "Aquarius": {"element": "air", "planet": "Saturn"},
    "Pisces": {"element": "water", "planet": "Jupiter"},
}

# Celestial event keywords
CELESTIAL_KEYWORDS = {
    "planets": ["Soleil", "Lune", "Mars", "Mercure", "Jupiter", "Venus", "Saturn"],
    "zodiac": list(ZODIAC_SIGNS.keys()),
    "aspects": ["conjonction", "opposition", "trine", "carre", "sextile",
                "conj", "opp", "tri", "qua", "sex"],
    "celestial": ["astre", "etoile", "planete", "ciel", "lune", "soleil",
                  "astre", "rayon", "eclipse", "comete", "meteore"],
}


def extract_celestial_references(text: str) -> List[Dict]:
    """Extract all celestial body references from text."""
    text_lower = text.lower()
    references = []

    # Planets
    for planet in CELESTIAL_KEYWORDS["planets"]:
        planet_lower = planet.lower()
        if planet_lower in text_lower:
            count = text_lower.count(planet_lower)
            references.append({
                "type": "planet",
                "name": planet,
                "count": count,
                "symbolism": PLANET_SYMBOLISM.get(planet, {}).get("meaning", "unknown"),
                "events": PLANET_SYMBOLISM.get(planet, {}).get("events", [])
            })

    # Zodiac signs
    for sign in CELESTIAL_KEYWORDS["zodiac"]:
        sign_lower = sign.lower()
        if sign_lower in text_lower:
            count = text_lower.count(sign_lower)
            references.append({
                "type": "zodiac",
                "name": sign,
                "count": count,
                "element": ZODIAC_SIGNS[sign]["element"],
                "ruler": ZODIAC_SIGNS[sign]["planet"]
            })

    # Aspects
    for aspect in CELESTIAL_KEYWORDS["aspects"]:
        if aspect in text_lower:
            references.append({
                "type": "aspect",
                "name": aspect,
                "count": 1
            })

    # Other celestial
    for keyword in CELESTIAL_KEYWORDS["celestial"]:
        if keyword in text_lower:
            # Avoid double-counting planets already found
            if not any(r["type"] == "planet" and r["name"].lower() == keyword for r in references):
                references.append({
                    "type": "celestial",
                    "name": keyword,
                    "count": text_lower.count(keyword)
                })

    return references


def interpret_astrological_vector(references: List[Dict]) -> Dict:
    """
    Interpret extracted celestial references to determine:
    - dominant_planet: The planet with most mentions
    - themes: Event categories suggested by planetary alignments
    - augury: Overall astrological judgment
    """
    if not references:
        return {"dominant_planet": None, "themes": [], "augury": "neutral"}

    # Count by type
    planet_refs = [r for r in references if r["type"] == "planet"]
    zodiac_refs = [r for r in references if r["type"] == "zodiac"]

    # Dominant planet
    dominant = None
    max_count = 0
    for ref in planet_refs:
        if ref["count"] > max_count:
            max_count = ref["count"]
            dominant = ref["name"]

    # Collect themes
    themes = []
    for ref in planet_refs:
        themes.extend(ref.get("events", []))
    for ref in references:
        if ref["type"] == "zodiac":
            themes.append(f"{ref['name']} ({ref['element']})")

    # Determine augury based on dominant planet
    augury = "neutral"
    if dominant:
        if dominant in ["Mars", "Soleil"]:
            augury = "bellicose"  # war-like
        elif dominant in ["Jupiter", "Venus"]:
            augury = "prosperous"  # positive
        elif dominant in ["Saturn"]:
            augury = "somber"  # restrictive
        elif dominant == "Lune":
            augury = "changeable"  # unstable

    return {
        "dominant_planet": dominant,
        "themes": list(set(themes))[:5],  # dedupe, limit to 5
        "augury": augury
    }


def infer_astrological_config(text: str) -> Dict:
    """
    Main astrology analysis entry point.

    Extracts celestial references and interprets their astrological meaning.

    Args:
        text: French text of the quatrain

    Returns:
        Dict with: references (list), interpretation (dict), reference_count
    """
    references = extract_celestial_references(text)
    interpretation = interpret_astrological_vector(references)

    return {
        "references": references,
        "interpretation": interpretation,
        "reference_count": len(references)
    }
