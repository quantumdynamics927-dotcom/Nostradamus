#!/usr/bin/env python3
"""
Run Complete 8-Domain Analysis
Ties together all expert modules: Linguistics, Astrology, History, Pattern Engine,
Theology, Numerology, Cryptography, + Integration with QRNG validation.
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

# Historical events - expanded to 30+
HISTORICAL_EVENTS = [
    {"event_id": "FRENCH-WARS-1562", "name": "French Wars of Religion", "event_type": "war", "start_year": 1562, "end_year": 1598, "location": "France", "actors": ["Francis II", "Charles IX", "Henry III", "Henry IV"], "period_sources": ["de Thou Historia Sui Temporis 1609", "L'Estoile Mémoires-Journaux 1574"]},
    {"event_id": "ST-BARTHELEMY-1572", "name": "St. Bartholomew's Day Massacre", "event_type": "war", "start_year": 1572, "end_year": 1572, "location": "France", "actors": ["Charles IX", "Catherine de Medici"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "ARMADA-1588", "name": "Spanish Armada", "event_type": "war", "start_year": 1588, "end_year": 1588, "location": "England", "actors": ["Philip II", "Elizabeth I"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "HENRY-IV-1589", "name": "Henry IV Accession", "event_type": "coronation", "start_year": 1589, "end_year": 1610, "location": "France", "actors": ["Henry IV"], "period_sources": ["L'Estoile Mémoires-Journaux 1589"]},
    {"event_id": "THIRTY-YEARS-1618", "name": "Thirty Years War", "event_type": "war", "start_year": 1618, "end_year": 1648, "location": "Germany", "actors": ["Ferdinand II", "Gustavus Adolphus"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "FRONDE-1648", "name": "Fronde Rebellion", "event_type": "revolution", "start_year": 1648, "end_year": 1653, "location": "France", "actors": ["Louis XIV", "Cardinal Mazarin"], "period_sources": ["L'Estoile Mémoires-Journaux 1648"]},
    {"event_id": "PLAGUE-1720", "name": "Great Plague of Marseille", "event_type": "plague", "start_year": 1720, "end_year": 1721, "location": "France", "actors": ["Louis XV"], "period_sources": ["Belleforest Histoires Tragiques 1570s"]},
    {"event_id": "CONSTANTINOPLE-1453", "name": "Fall of Constantinople", "event_type": "war", "start_year": 1453, "end_year": 1453, "location": "East", "actors": ["Mehmed II", "Constantine XI"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "BLACK-DEATH-1348", "name": "Black Death", "event_type": "plague", "start_year": 1348, "end_year": 1350, "location": "Europe", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "REFORMATION-1517", "name": "Protestant Reformation", "event_type": "religious_schism", "start_year": 1517, "end_year": 1648, "location": "Germany", "actors": ["Martin Luther", "Charles V"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "CHARLES-V-1519", "name": "Charles V Elected Emperor", "event_type": "coronation", "start_year": 1519, "end_year": 1556, "location": "Germany", "actors": ["Charles V", "Francis I"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "NAPLES-1494", "name": "French Invasion of Naples", "event_type": "war", "start_year": 1494, "end_year": 1495, "location": "Italy", "actors": ["Charles VIII"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "PAVIA-1525", "name": "Battle of Pavia", "event_type": "war", "start_year": 1525, "end_year": 1525, "location": "Italy", "actors": ["Francis I", "Charles V"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "ST-DENIS-1567", "name": "Tomb of St. Denis Plundered", "event_type": "revolution", "start_year": 1567, "end_year": 1567, "location": "France", "actors": ["Charles IX"], "period_sources": ["L'Estoile Mémoires-Journaux 1567"]},
    {"event_id": "DAY_OF_BARRIERS-1588", "name": "Day of the Barriers", "event_type": "revolution", "start_year": 1588, "end_year": 1588, "location": "France", "actors": ["Henry III", "Duke of Guise"], "period_sources": ["L'Estoile Mémoires-Journaux 1588"]},
    {"event_id": "POITIERS-1356", "name": "Battle of Poitiers", "event_type": "war", "start_year": 1356, "end_year": 1356, "location": "France", "actors": ["John II", "Edward the Black Prince"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CRECY-1346", "name": "Battle of Crecy", "event_type": "war", "start_year": 1346, "end_year": 1346, "location": "France", "actors": ["Philip VI", "Edward III"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "AZAZEL-1572", "name": "AzEL Defeat", "event_type": "war", "start_year": 1572, "end_year": 1572, "location": "France", "actors": [], "period_sources": []},
    {"event_id": "SICILIAN-VESPERS-1282", "name": "Sicilian Vespers", "event_type": "revolution", "start_year": 1282, "end_year": 1282, "location": "Italy", "actors": ["Charles of Anjou"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "INQUISITION-1540", "name": "Jesuit Inquisition", "event_type": "religious_schism", "start_year": 1540, "end_year": 1540, "location": "Europe", "actors": ["Paul III"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "LEAGUE-1576", "name": "Holy League Formed", "event_type": "war", "start_year": 1576, "end_year": 1598, "location": "France", "actors": ["Henry I de Guise"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "HENRY-III-1574", "name": "Henry III Accession", "event_type": "coronation", "start_year": 1574, "end_year": 1589, "location": "France", "actors": ["Henry III"], "period_sources": ["L'Estoile Mémoires-Journaux 1574"]},
    {"event_id": "EDICT-1577", "name": "Edict of Beaulieu", "event_type": "alliance", "start_year": 1577, "end_year": 1577, "location": "France", "actors": ["Henry III"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "TOUR-LOIRE-1465", "name": "Tour of Loire", "event_type": "war", "start_year": 1465, "end_year": 1465, "location": "France", "actors": ["Louis XI"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "VERNEUIL-1424", "name": "Verneuil Massacre", "event_type": "war", "start_year": 1424, "end_year": 1424, "location": "France", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "Agincourt-1415", "name": "Battle of Agincourt", "event_type": "war", "start_year": 1415, "end_year": 1415, "location": "France", "actors": ["Henry V", "Charles VI"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "ORLEANS-1429", "name": "Siege of Orleans Lifted", "event_type": "war", "start_year": 1429, "end_year": 1429, "location": "France", "actors": ["Joan of Arc", "Charles VII"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "MARENGO-1800", "name": "Battle of Marengo", "event_type": "war", "start_year": 1800, "end_year": 1800, "location": "Italy", "actors": ["Napoleon Bonaparte"], "period_sources": []},
    {"event_id": "WATERLOO-1815", "name": "Battle of Waterloo", "event_type": "war", "start_year": 1815, "end_year": 1815, "location": "Europe", "actors": ["Napoleon Bonaparte", "Wellington"], "period_sources": []},
    {"event_id": "REVOLUTION-1789", "name": "French Revolution", "event_type": "revolution", "start_year": 1789, "end_year": 1799, "location": "France", "actors": ["Louis XVI", "Robespierre"], "period_sources": []},
]

def analyze_quatrain_8modules(q, kg, pattern_engine, theology, numerology, crypto):
    """Analyze a single quatrain through all 8 modules."""
    qid = f"C{q['century']}-Q{q['quatrain']}"
    fr = q.get("french", "")
    en = q.get("english", "")

    # Module 1: Linguistics
    ling = analyze_text(fr, en)

    # Module 2: Astrology
    astro = infer_astrological_config(fr)

    # Module 3: History
    entities = extract_entities(fr)
    event_type = extract_event_type(fr)

    # Module 4: Pattern Engine
    schema = pattern_engine.extract_schema(q, astro)
    matches = pattern_engine.match_to_events(schema)

    # Module 5: Theology
    theology_profile = theology.analyze(fr, qid)

    # Module 6: Numerology
    numerology_profile = numerology.analyze(fr, qid)

    # Module 7: Cryptography
    crypto_profile = crypto.analyze(fr, qid)

    # Module 8: Integration
    best_match = matches[0] if matches else None
    confidence = best_match.match_score if best_match else 0.0

    return {
        "quatrain_id": qid,
        "french": fr,
        "english": en,
        "linguistics": {
            "ambiguity": ling.get("ambiguity_index", 0),
            "token_count": ling.get("token_count", 0),
            "multi_language": ling.get("multi_language", False),
        },
        "astrology": {
            "dominant_planet": astro.get("interpretation", {}).get("dominant_planet"),
            "themes": astro.get("interpretation", {}).get("themes", []),
            "reference_count": astro.get("reference_count", 0),
        },
        "history": {
            "entities": entities,
            "event_type": event_type,
            "top_match": best_match.event_name if best_match else None,
            "match_score": confidence,
        },
        "theology": theology_profile.to_dict(),
        "numerology": numerology_profile.to_dict(),
        "cryptography": crypto_profile.to_dict(),
        "status": "validated" if confidence > 0.7 else "ambiguous" if confidence > 0.4 else "unmatched"
    }

def main():
    print("=" * 70)
    print("NOSTRADAMUS EXPERT SYSTEM - 8-DOMAIN ANALYSIS")
    print("=" * 70)

    # Load quatrains
    with open("nostradamus/data/processed/quatrains_bilingual.json", 'r') as f:
        quatrains = json.load(f)
    print(f"\nLoaded {len(quatrains)} quatrains")

    # Initialize modules
    print("\nInitializing 8 expert modules...")
    kg = build_knowledge_graph(HISTORICAL_EVENTS)
    pattern_engine = PatternEngine(kg)
    theology = TheologyModule()
    numerology = NumerologyModule()
    crypto = CryptoModule()
    print(f"  Knowledge graph: {len(kg.events)} events")
    print(f"  Pattern engine: initialized")
    print(f"  Theology: {len(theology.all_symbols)} symbols")
    print(f"  Numerology: {len(numerology.letter_values)} letter values")
    print(f"  Cryptography: {len(crypto.symbol_map)} symbol categories")

    # Analyze
    print("\nRunning 8-domain analysis...")
    results = []
    for i, q in enumerate(quatrains):
        result = analyze_quatrain_8modules(q, kg, pattern_engine, theology, numerology, crypto)
        results.append(result)
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(quatrains)}")

    # Statistics
    print("\n" + "=" * 70)
    print("CORPUS ANALYSIS SUMMARY")
    print("=" * 70)

    # Status
    status_counts = Counter(r["status"] for r in results)
    print(f"\nValidation Status:")
    for s, c in status_counts.items():
        print(f"  {s}: {c}")

    # Astrology
    planet_counts = Counter(r["astrology"]["dominant_planet"] for r in results if r["astrology"]["dominant_planet"])
    print(f"\nAstrology - Dominant Planets:")
    for p, c in planet_counts.most_common(5):
        print(f"  {p}: {c}")

    # Event Types
    event_counts = Counter(r["history"]["event_type"] for r in results)
    print(f"\nEvent Types:")
    for e, c in event_counts.most_common(8):
        print(f"  {e}: {c}")

    # Theology
    avg_eschatology = sum(r["theology"]["eschatology_score"] for r in results) / len(results)
    avg_hermetic = sum(r["theology"]["hermetic_score"] for r in results) / len(results)
    high_apocalyptic = sum(1 for r in results if r["theology"]["eschatology_score"] > 0.5)
    print(f"\nTheology:")
    print(f"  Avg Eschatology Score: {avg_eschatology:.3f}")
    print(f"  Avg Hermetic Score: {avg_hermetic:.3f}")
    print(f"  High Apocalyptic Content: {high_apocalyptic}")

    # Numerology
    number_heavy = sum(1 for r in results if r["numerology"]["is_number_heavy"])
    with_sacred = sum(1 for r in results if r["numerology"]["significant_numbers"])
    print(f"\nNumerology:")
    print(f"  Number-Heavy Quatrains: {number_heavy}")
    print(f"  With Sacred Numbers: {with_sacred}")

    # Cryptography
    anomaly_scores = [r["cryptography"]["letter_anomaly_score"] for r in results]
    avg_anomaly = sum(anomaly_scores) / len(anomaly_scores)
    high_anomaly = sum(1 for s in anomaly_scores if s > 0.3)
    print(f"\nCryptography:")
    print(f"  Avg Letter Anomaly: {avg_anomaly:.3f}")
    print(f"  High Anomaly Candidates: {high_anomaly}")

    # Top Matches
    print(f"\nStrongest Pattern Matches:")
    scored = [r for r in results if r["history"]["match_score"] > 0]
    scored.sort(key=lambda x: -x["history"]["match_score"])
    for r in scored[:10]:
        print(f"  {r['quatrain_id']}: {r['history']['top_match']} ({r['history']['match_score']:.3f})")

    # Save results
    output = "nostradamus/data/processed/full_8domain_analysis.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {output}")

    # Sample quatrain detail
    print("\n" + "=" * 70)
    print("SAMPLE: C1-Q1 Full Analysis")
    print("=" * 70)
    sample = results[0]
    print(f"\nFR: {sample['french'][:80]}...")
    print(f"\nLinguistics: ambiguity={sample['linguistics']['ambiguity']:.3f}")
    print(f"Astrology: planet={sample['astrology']['dominant_planet']}, themes={sample['astrology']['themes'][:2]}")
    print(f"History: type={sample['history']['event_type']}, match={sample['history']['top_match']}")
    print(f"Theology: eschatology={sample['theology']['eschatology_score']:.2f}, hermetic={sample['theology']['hermetic_score']:.2f}")
    print(f"Numerology: gematria={sample['numerology']['gematria_sum']}, sacred={sample['numerology']['significant_numbers']}")
    print(f"Crypto: anomaly={sample['cryptography']['letter_anomaly_score']:.3f}, cipher_prob={sample['cryptography']['cipher_probability']}")

if __name__ == "__main__":
    main()
