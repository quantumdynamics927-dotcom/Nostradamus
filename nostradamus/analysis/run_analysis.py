#!/usr/bin/env python3
"""
Run full expert analysis on all quatrains.
3 modules: Linguistics, Astrology, History.
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent))

from domains import (
    analyze_text, extract_entities, extract_event_type,
    infer_astrological_config, match_to_events, validate_prediction,
    PERIOD_SOURCES
)

# Sample historical events (period sources only)
EVENTS = [
    {
        "event_id": "FRENCH-WARS-1562",
        "name": "French Wars of Religion",
        "start_date": "1562-03-01",
        "end_date": "1598-04-03",
        "event_type": "war",
        "location": {"country": "France", "region": "France"},
        "actors": [
            {"Name": "Francis II", "role": "king"},
            {"Name": "Charles IX", "role": "king"},
            {"Name": "Henry III", "role": "king"},
            {"Name": "Henry IV", "role": "king"}
        ],
        "period_sources": [
            {"name": "de Thou", "year": 1609, "quote": "..."}
        ]
    },
    {
        "event_id": "ST-BARTHELEMY-1572",
        "name": "St. Bartholomew's Day Massacre",
        "start_date": "1572-08-24",
        "end_date": "1572-10-03",
        "event_type": "war",
        "location": {"country": "France", "region": "Paris"},
        "actors": [
            {"Name": "Charles IX", "role": "king"},
            {"Name": "Catherine de Medici", "role": "queen mother"}
        ],
        "period_sources": [
            {"name": "de Thou", "year": 1609, "quote": "..."},
            {"name": "L'Estoile", "year": 1572, "quote": "..."}
        ]
    },
    {
        "event_id": "ARMADA-1588",
        "name": "Spanish Armada",
        "start_date": "1588-05-30",
        "end_date": "1588-08-08",
        "event_type": "battle",
        "location": {"country": "England", "region": "English Channel"},
        "actors": [
            {"Name": "Philip II", "role": "king of Spain"},
            {"Name": "Elizabeth I", "role": "queen of England"}
        ],
        "period_sources": [
            {"name": "de Thou", "year": 1609, "quote": "..."}
        ]
    },
    {
        "event_id": "HENRY-IV-1589",
        "name": "Henry IV Accession",
        "start_date": "1589-08-02",
        "end_date": "1610-05-14",
        "event_type": "coronation",
        "location": {"country": "France", "region": "France"},
        "actors": [{"Name": "Henry IV", "role": "king"}],
        "period_sources": [
            {"name": "L'Estoile", "year": 1589, "quote": "..."}
        ]
    },
    {
        "event_id": "THIRTY-YEARS-1618",
        "name": "Thirty Years War",
        "start_date": "1618-05-23",
        "end_date": "1648-10-24",
        "event_type": "war",
        "location": {"country": "Europe", "region": "Central Europe"},
        "actors": [
            {"Name": "Ferdinand II", "role": "Holy Roman Emperor"},
            {"Name": "Gustavus Adolphus", "role": "King of Sweden"}
        ],
        "period_sources": [
            {"name": "de Thou", "year": 1609, "quote": "..."}
        ]
    },
    {
        "event_id": "FRONDE-1648",
        "name": "Fronde Rebellion",
        "start_date": "1648-05-15",
        "end_date": "1653-10-05",
        "event_type": "revolution",
        "location": {"country": "France", "region": "France"},
        "actors": [{"Name": "Louis XIV", "role": "king"}],
        "period_sources": [
            {"name": "L'Estoile", "year": 1648, "quote": "..."}
        ]
    },
    {
        "event_id": "PLAGUE-1720",
        "name": "Great Plague of Marseille",
        "start_date": "1720-06-01",
        "end_date": "1721-10-01",
        "event_type": "plague",
        "location": {"country": "France", "region": "Marseille"},
        "actors": [{"Name": "Louis XV", "role": "king"}],
        "period_sources": [
            {"name": "Belleforest", "year": 1720, "quote": "..."}
        ]
    }
]

def analyze_quatrain(quatrain):
    fr = quatrain["french"]
    en = quatrain["english"]
    qid = f"{quatrain['century']}-{quatrain['quatrain']}"

    # 1. Linguistics
    ling = analyze_text(fr, en)

    # 2. Astrology
    astro = infer_astrological_config(fr)

    # 3. History
    entities = extract_entities(fr)
    event_type = extract_event_type(fr)

    prediction = {
        "entities": entities,
        "location": {"country": "France"},
        "what": event_type
    }
    matches = match_to_events(prediction, EVENTS)

    return {
        "id": qid,
        "century": quatrain["century"],
        "quatrain_num": quatrain["quatrain"],
        "french": fr,
        "english": en,
        "linguistics": {
            "ambiguity": ling["ambiguity_index"],
            "multi_language": ling["multi_language"],
            "token_count": ling["token_count"]
        },
        "astrology": {
            "reference_count": astro["reference_count"],
            "dominant_planet": astro["interpretation"].get("dominant_planet"),
            "themes": astro["interpretation"].get("themes", [])
        },
        "history": {
            "entities": len(entities),
            "event_type": event_type,
            "top_match": matches[0]["event_name"] if matches else None,
            "match_score": matches[0]["score"]["composite"] if matches else 0.0,
            "period_sources": matches[0]["period_sources"] if matches else []
        },
        "status": "validated" if (matches and matches[0]["score"]["composite"] > 0.7) else
                  "ambiguous" if (matches and matches[0]["score"]["composite"] > 0.4) else "unmatched"
    }

def main():
    # Load quatrains
    with open("nostradamus/data/processed/quatrains_bilingual.json", 'r') as f:
        quatrains = json.load(f)

    print(f"Analyzing {len(quatrains)} quatrains...")

    results = []
    for i, q in enumerate(quatrains):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(quatrains)}")
        results.append(analyze_quatrain(q))

    # Save
    output_path = "nostradamus/data/processed/quatrains_analyzed.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output_path}")

    # Stats
    ambig_by_c = Counter(r["linguistics"]["ambiguity"] for r in results)
    planet_by_c = Counter(r["astrology"]["dominant_planet"] for r in results if r["astrology"]["dominant_planet"])
    status_counts = Counter(r["status"] for r in results)

    print("\n=== ANALYSIS SUMMARY ===")
    print(f"Total: {len(results)} quatrains")
    print(f"\nStatus:")
    for s, c in status_counts.items():
        print(f"  {s}: {c}")
    print(f"\nAstrology - Dominant planets:")
    for p, c in planet_by_c.most_common(5):
        print(f"  {p}: {c}")
    print(f"\nLinguistics - Avg ambiguity: {sum(r['linguistics']['ambiguity'] for r in results)/len(results):.3f}")

    # Show samples
    print("\n=== SAMPLE RESULTS ===")
    for qid in ["I-1", "I-2", "VIII-69", "X-100"]:
        r = next((x for x in results if x["id"] == qid), None)
        if r:
            print(f"\n{qid}:")
            print(f"  FR: {r['french'][:60]}...")
            print(f"  Ambiguity: {r['linguistics']['ambiguity']:.2f}")
            print(f"  Planet: {r['astrology']['dominant_planet']}")
            print(f"  Type: {r['history']['event_type']}")
            print(f"  Match: {r['history']['top_match']} ({r['history']['match_score']:.2f})")
            print(f"  Status: {r['status']}")

if __name__ == "__main__":
    main()
