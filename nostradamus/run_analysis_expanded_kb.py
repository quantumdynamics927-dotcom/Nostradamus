#!/usr/bin/env python3
"""
Run Complete 8-Domain Analysis with Expanded KB (87 events)
"""

import json
import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from domains import (
    analyze_text, infer_astrological_config, extract_entities, extract_event_type,
    TheologyModule, NumerologyModule, CryptoModule
)
from pattern_engine import PatternEngine, build_knowledge_graph, EventType, Region

# Import expanded KB
sys.path.insert(0, str(Path(__file__).parent / "data"))
from historical_events_kb import HISTORICAL_EVENTS_KB

def analyze_quatrain(q, kg, pattern_engine, theology, numerology, crypto):
    qid = f"C{q['century']}-Q{q['quatrain']}"
    fr = q.get("french", "")

    ling = analyze_text(fr, "")
    astro = infer_astrological_config(fr)
    entities = extract_entities(fr)
    event_type = extract_event_type(fr)
    schema = pattern_engine.extract_schema(q, astro)
    matches = pattern_engine.match_to_events(schema)
    theology_profile = theology.analyze(fr, qid)
    numerology_profile = numerology.analyze(fr, qid)
    crypto_profile = crypto.analyze(fr, qid)

    best = matches[0] if matches else None
    confidence = best.match_score if best else 0.0

    return {
        "quatrain_id": qid,
        "french": fr,
        "linguistics": {"ambiguity": ling.get("ambiguity_index", 0), "token_count": ling.get("token_count", 0)},
        "astrology": {"dominant_planet": astro.get("interpretation", {}).get("dominant_planet"), "themes": astro.get("interpretation", {}).get("themes", [])},
        "history": {"entities": entities, "event_type": event_type, "top_match": best.event_name if best else None, "match_score": confidence},
        "theology": theology_profile.to_dict(),
        "numerology": numerology_profile.to_dict(),
        "cryptography": crypto_profile.to_dict(),
        "status": "validated" if confidence > 0.7 else "ambiguous" if confidence > 0.4 else "unmatched"
    }

def main():
    print("=" * 70)
    print("NOSTRADAMUS 8-DOMAIN ANALYSIS - EXPANDED KB (87 EVENTS)")
    print("=" * 70)

    with open("nostradamus/data/processed/quatrains_bilingual.json", 'r') as f:
        quatrains = json.load(f)
    print(f"\nLoaded {len(quatrains)} quatrains")

    print("\nInitializing modules...")
    kg = build_knowledge_graph(HISTORICAL_EVENTS_KB)
    pattern_engine = PatternEngine(kg)
    theology = TheologyModule()
    numerology = NumerologyModule()
    crypto = CryptoModule()
    print(f"  KB: {len(kg.events)} events, {len(kg.cycles)} cycles")

    print("\nRunning analysis...")
    results = []
    for i, q in enumerate(quatrains):
        r = analyze_quatrain(q, kg, pattern_engine, theology, numerology, crypto)
        results.append(r)
        if i % 100 == 0:
            print(f"  {i}/{len(quatrains)}")

    # Statistics
    print("\n" + "=" * 70)
    print("CORPUS SUMMARY")
    print("=" * 70)

    status_counts = Counter(r["status"] for r in results)
    print(f"\nValidation Status:")
    for s, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")

    planets = Counter(r["astrology"]["dominant_planet"] for r in results if r["astrology"]["dominant_planet"])
    print(f"\nTop Planets: {', '.join(f'{p}({c})' for p, c in planets.most_common(5))}")

    events = Counter(r["history"]["event_type"] for r in results)
    print(f"\nEvent Types: {dict(events.most_common(8))}")

    theology_avg = sum(r["theology"]["eschatology_score"] for r in results) / len(results)
    crypto_high = sum(1 for r in results if r["cryptography"]["letter_anomaly_score"] > 0.3)
    print(f"\nTheology avg eschatology: {theology_avg:.3f}")
    print(f"Crypto high anomaly: {crypto_high}/951 ({100*crypto_high/951:.1f}%)")

    # Top matches
    print(f"\nTop 15 Pattern Matches:")
    scored = [r for r in results if r["history"]["match_score"] > 0]
    scored.sort(key=lambda x: -x["history"]["match_score"])
    for r in scored[:15]:
        print(f"  {r['quatrain_id']}: {r['history']['top_match']} ({r['history']['match_score']:.3f}) - {r['history']['event_type']}")

    # Event type match distribution
    print(f"\nEvent Type Matches:")
    matched = [r for r in results if r["history"]["match_score"] > 0]
    matched_types = Counter(r["history"]["event_type"] for r in matched)
    for et, c in matched_types.most_common():
        print(f"  {et}: {c}")

    # Save
    output = "nostradamus/data/processed/full_analysis_expanded_kb.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output}")

    # Show sample high-anomaly crypto
    print("\n" + "=" * 70)
    print("HIGHEST CRYPTOGRAPHIC ANOMALY QUATRAINS")
    print("=" * 70)
    scored_crypto = sorted(results, key=lambda x: -x["cryptography"]["letter_anomaly_score"])
    for r in scored_crypto[:5]:
        print(f"\n{r['quatrain_id']}: anomaly={r['cryptography']['letter_anomaly_score']:.3f}")
        print(f"  FR: {r['french'][:70]}...")

if __name__ == "__main__":
    main()
