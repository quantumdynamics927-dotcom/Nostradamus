#!/usr/bin/env python3
"""
History Module for Nostradamus Prophecies
Period source matching using only de Thou, L'Estoile, Froissart, Belleforest.
Tier 1 source compliance - no Wikipedia or modern encyclopedias.
"""

import re
from typing import Dict, List

# Period Sources Index - Tier 1 Chronicles
# These are 16th-17th century sources CONTEMPORARY to Nostradamus
PERIOD_SOURCES = {
    "de Thou": {
        "work": "Historia Sui Temporis",
        "years": "1609",
        "tier": 1,
        "description": "Jacques Auguste de Thou's universal history 1543-1607"
    },
    "L'Estoile": {
        "work": "Mémoires-Journaux",
        "years": "1574-1611",
        "tier": 1,
        "description": "Pierre de L'Estoile's personal diary of French Wars of Religion"
    },
    "Froissart": {
        "work": "Chroniques",
        "years": "1480s",
        "tier": 1,
        "description": "Jean Froissart's chronicle of 14th century wars"
    },
    "Belleforest": {
        "work": "Histoires Tragiques",
        "years": "1570s",
        "tier": 2,
        "description": "Francois de Belleforest's expansion of Bandello"
    },
}

# Event type keywords
EVENT_TYPES = {
    "war": ["guerre", "bataille", "combat", "siege", "armee", "soldats",
            "militaire", "invasion", "conquete", "defait", "vaincu"],
    "pestilence": ["peste", "plague", "maladie", "epidemie", "contagion",
                   "fievre", "mort", "deces", "funeste"],
    "famine": ["famine", "disette", "faute de pain", "reve", "sterilite",
               "mes harveste", "escour", "ble"],
    "coronation": ["couronne", "roy", "roi", "coronation", "sacré", "majeste",
                   "regne", "sceptre", "trone"],
    "revolution": ["revolte", "revolution", "emeute", "sedition", "trouble",
                   " Rebellion ", "soulvement", "conjuration"],
    "alliance": ["alliance", "mariage", "union", "traite", "paix", "negociation",
                 "ambassade", "ambasadeurs"],
    "eclipse": ["eclipse", "obscurcissement", "tenebres", "soleil noir", "lune sang"],
    "flood": ["inondation", "deluge", "pluie", "eaux", "grece", "fleuve"],
    # Natural Disasters
    "earthquake": ["terre trembler", "tremblement", "terremotus", "secousse",
                   "la terre movra", "la terre s esmouvra"],
    "tsunami": ["vague grand", "mer monter", "inondation marin", "tsunami"],
    "volcanic": ["feu grond", "volcan", "montagne flamber", "lave couler",
                 "ember z", "braz"],
    "wildfire": ["forest brusler", "flamber", "feu grand", "incend", "braslar"],
    "drought": ["secheresse", "chaleur grand", "eaux manque", "siccite",
                "aridite", "sans pluye"],
    # Space / Planetary
    "solar_storm": ["aurore", "flammes ciel", "coron", "masse solaire",
                    "vent solaire", "aurora borealis"],
    "asteroid": ["astre cheoir", "pierre ciel", "asteroid", "meteor", "meteorite"],
    "comet": ["comete", "trouble estoille", "estoille queue", "queue estoille",
              "chevelure estoille"],
}

# Location keywords
LOCATION_KEYWORDS = {
    "France": ["france", "francais", "gall", "gaulois", " paris", "lyon",
               "marseille", "rouen", "bordeaux", "tour", "loire"],
    "England": ["angleterre", "anglais", "londres", "mer du nord", "canal"],
    "Spain": ["espagne", "espagnol", "madrid", "ibere", "iberia"],
    "Italy": ["italie", "italien", "rome", "florence", "milan", "venise"],
    "Germany": ["allemagne", "allemand", "germain", "germanique", "vienne"],
    "Europe": ["europe", "chreste", "chrestien", "chretiente", "christol",
               "foy", "fidel", "latin", "romain"],
    "Ottoman": ["turc", "ottoman", "constantin", "byzance", "sulta", "turquois"],
    "Mediterranean": ["mediterranee", "mer", "port", "cote", "navire", "marine"],
}


def extract_entities(text: str) -> List[str]:
    """Extract named entities (places, people, countries) from text."""
    text_lower = text.lower()
    entities = []

    # Countries
    for country, keywords in LOCATION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                entities.append(country)
                break

    # Roman numerals for centuries/quantities
    roman_numerals = re.findall(r'\b[IVXLCDM]+\b', text)
    entities.extend(roman_numerals)

    return list(set(entities))


def extract_event_type(text: str) -> str:
    """Classify the event type based on keyword analysis."""
    text_lower = text.lower()
    scores = {}

    for event_type, keywords in EVENT_TYPES.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[event_type] = score

    if not scores:
        return "unknown"
    return max(scores, key=scores.get)


def compute_match_score(prediction: Dict, event: Dict) -> Dict:
    """
    Compute composite match score between a quatrain prediction and historical event.

    Scoring weights:
    - entity_match: 0.3 (geographical/actor overlap)
    - location_match: 0.3 (country/region match)
    - type_match: 0.4 (event type similarity)

    Returns Dict with score components and composite score.
    """
    entity_score = 0.0
    location_score = 0.0
    type_score = 0.0

    pred_entities = prediction.get("entities", [])
    event_actors = [a.get("Name", a.get("name", "")).lower() for a in event.get("actors", [])]

    # Entity match
    for ent in pred_entities:
        if ent.lower() in event_actors:
            entity_score = 1.0
            break
        # Roman numeral match (century)
        if ent in event.get("event_id", ""):
            entity_score = 0.5

    # Location match
    pred_location = prediction.get("location", {})
    event_location = event.get("location", {})

    if pred_location.get("country") == event_location.get("country"):
        location_score = 1.0
    elif pred_location.get("region") == event_location.get("region"):
        location_score = 0.7

    # Type match
    pred_type = prediction.get("what")
    event_type = event.get("event_type")

    if pred_type and event_type:
        if pred_type.lower() == event_type.lower():
            type_score = 1.0
        elif pred_type in ["war", "battle"] and event_type in ["war", "battle", "revolution"]:
            type_score = 0.7
        elif pred_type in ["plague", "pestilence"] and event_type == "plague":
            type_score = 1.0

    composite = entity_score * 0.3 + location_score * 0.3 + type_score * 0.4

    return {
        "entity_score": entity_score,
        "location_score": location_score,
        "type_score": type_score,
        "composite": round(composite, 3),
        "matched_on": {
            "entities": entity_score > 0,
            "location": location_score > 0,
            "type": type_score > 0
        }
    }


def match_to_events(prediction: Dict, events: List[Dict]) -> List[Dict]:
    """
    Match a quatrain prediction against known historical events.

    Returns sorted list of matches with scores, highest first.
    """
    matches = []

    for event in events:
        score = compute_match_score(prediction, event)
        if score["composite"] > 0:
            matches.append({
                "event_id": event["event_id"],
                "event_name": event["name"],
                "score": score,
                "period_sources": event.get("period_sources", []),
                "start_date": event.get("start_date"),
                "end_date": event.get("end_date")
            })

    # Sort by composite score descending
    matches.sort(key=lambda x: x["score"]["composite"], reverse=True)
    return matches


def validate_prediction(quatrain_id: str, predictions: List[Dict], events: List[Dict]) -> Dict:
    """
    Validate a quatrain prediction against historical events.

    Returns validation status:
    - validated: score > 0.7 (strong match)
    - ambiguous: score 0.4-0.7 (partial match)
    - no_match: score < 0.4
    - anachronism_detected: requires post-1700 knowledge
    """
    if not predictions:
        return {"status": "no_match", "quatrain_id": quatrain_id, "matches": []}

    best_matches = []
    for pred in predictions:
        matches = match_to_events(pred, events)
        if matches:
            best_matches.append(matches[0])

    if not best_matches:
        return {"status": "no_match", "quatrain_id": quatrain_id, "matches": []}

    # Get best overall match
    best = max(best_matches, key=lambda x: x["score"]["composite"])
    score = best["score"]["composite"]

    if score > 0.7:
        status = "validated"
    elif score > 0.4:
        status = "ambiguous"
    else:
        status = "no_match"

    return {
        "status": status,
        "quatrain_id": quatrain_id,
        "matches": best_matches,
        "best_match": best,
        "confidence": score
    }
