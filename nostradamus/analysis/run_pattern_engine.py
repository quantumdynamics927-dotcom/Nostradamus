#!/usr/bin/env python3
"""
Run complete Nostradamus Pattern Engine Analysis
Ties together: extraction -> pattern engine -> knowledge graph -> cycle detection
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from pattern_engine import (
    PatternEngine, TemporalKnowledgeGraph, EventType, Region,
    HistoricalEvent, Cycle, build_knowledge_graph
)
from domains import (
    analyze_text, infer_astrological_config, extract_entities,
    extract_event_type, match_to_events
)

# === HISTORICAL EVENTS WITH PERIOD SOURCE CITATIONS ===

HISTORICAL_EVENTS = [
    # French Wars of Religion (1562-1598)
    {
        "event_id": "FRENCH-WARS-1562",
        "name": "French Wars of Religion",
        "event_type": "war",
        "start_year": 1562, "end_year": 1598,
        "location": "France",
        "actors": ["Francis II", "Charles IX", "Henry III", "Henry IV", "Catherine de Medici"],
        "period_sources": ["de Thou Historia Sui Temporis 1609", "L'Estoile Mémoires-Journaux 1574"],
        "related_events": ["ST-BARTHELEMY-1572", "HENRY-IV-1589"],
        "astrology_notes": "Mars prominent - wars"
    },
    {
        "event_id": "ST-BARTHELEMY-1572",
        "name": "St. Bartholomew's Day Massacre",
        "event_type": "war",
        "start_year": 1572, "end_year": 1572,
        "location": "France",
        "actors": ["Charles IX", "Catherine de Medici", "Admiral Coligny"],
        "period_sources": ["de Thou Historia Sui Temporis 1609", "L'Estoile Mémoires-Journaux 1572"],
        "astrology_notes": "Solar eclipse preceding - considered ill omen"
    },
    {
        "event_id": "ARMADA-1588",
        "name": "Spanish Armada",
        "event_type": "war",
        "start_year": 1588, "end_year": 1588,
        "location": "England",
        "actors": ["Philip II", "Elizabeth I", "Duke of Medina Sidonia"],
        "period_sources": ["de Thou Historia Sui Temporis 1609"],
        "related_events": ["HENRY-IV-1589"],
        "astrology_notes": "Saturn-Jupiter conjunction 1588"
    },
    {
        "event_id": "HENRY-IV-1589",
        "name": "Henry IV Accession",
        "event_type": "coronation",
        "start_year": 1589, "end_year": 1610,
        "location": "France",
        "actors": ["Henry IV", "Catherine de Medici"],
        "period_sources": ["L'Estoile Mémoires-Journaux 1589"],
        "astrology_notes": "Jupiter in Aries - expansion"
    },
    {
        "event_id": "THIRTY-YEARS-1618",
        "name": "Thirty Years War",
        "event_type": "war",
        "start_year": 1618, "end_year": 1648,
        "location": "Germany",
        "actors": ["Ferdinand II", "Gustavus Adolphus", "Richelieu"],
        "period_sources": ["de Thou Historia Sui Temporis 1609"],
        "astrology_notes": "Mars-Saturn conflict - prolonged war"
    },
    {
        "event_id": "FRONDE-1648",
        "name": "Fronde Rebellion",
        "event_type": "revolution",
        "start_year": 1648, "end_year": 1653,
        "location": "France",
        "actors": ["Louis XIV", "Cardinal Mazarin", "Prince de Conde"],
        "period_sources": ["L'Estoile Mémoires-Journaux 1648"],
        "astrology_notes": "Saturn in Cancer - restriction"
    },
    {
        "event_id": "PLAGUE-1720",
        "name": "Great Plague of Marseille",
        "event_type": "plague",
        "start_year": 1720, "end_year": 1721,
        "location": "France",
        "actors": ["Louis XV"],
        "period_sources": ["Belleforest Histoires Tragiques 1570s"],
        "astrology_notes": "Saturn prominent - death/limitation"
    },
    # Additional key events
    {
        "event_id": "CONSTANTINOPLE-1453",
        "name": "Fall of Constantinople",
        "event_type": "war",
        "start_year": 1453, "end_year": 1453,
        "location": "East",
        "actors": ["Mehmed II", "Constantine XI"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Eclipse 1453 - cosmic sign"
    },
    {
        "event_id": "SICILIAN-VESPERS-1282",
        "name": "Sicilian Vespers",
        "event_type": "revolution",
        "start_year": 1282, "end_year": 1282,
        "location": "Italy",
        "actors": ["Charles of Anjou"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Martial event"
    },
    {
        "event_id": "BLACK-DEATH-1348",
        "name": "Black Death",
        "event_type": "plague",
        "start_year": 1348, "end_year": 1350,
        "location": "Europe",
        "actors": [],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Saturn in Scorpio - plague"
    },
    {
        "event_id": "REFORMATION-1517",
        "name": "Protestant Reformation",
        "event_type": "religious_schism",
        "start_year": 1517, "end_year": 1648,
        "location": "Germany",
        "actors": ["Martin Luther", "Charles V"],
        "period_sources": ["de Thou Historia Sui Temporis 1609"],
        "astrology_notes": "Jupiter-Saturn conjunction"
    },
    {
        "event_id": "INQUISITION-1540",
        "name": "Jesuit Inquisition",
        "event_type": "religious_schism",
        "start_year": 1540, "end_year": 1540,
        "location": "Europe",
        "actors": ["Paul III"],
        "period_sources": ["de Thou Historia Sui Temporis 1609"],
        "astrology_notes": "Saturn prominent"
    },
    {
        "event_id": "CHARLES-V-1519",
        "name": "Charles V Elected Emperor",
        "event_type": "coronation",
        "start_year": 1519, "end_year": 1556,
        "location": "Germany",
        "actors": ["Charles V", "Francis I"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Jupiter in Leo - royal power"
    },
    {
        "event_id": "NAPLES-1494",
        "name": "French Invasion of Naples",
        "event_type": "war",
        "start_year": 1494, "end_year": 1495,
        "location": "Italy",
        "actors": ["Charles VIII", "Ferdinand II of Aragon"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Mars in Aries - invasion"
    },
    {
        "event_id": "MARIGNANO-1515",
        "name": "Battle of Marignano",
        "event_type": "war",
        "start_year": 1515, "end_year": 1515,
        "location": "Italy",
        "actors": ["Francis I", "Massimiliano Sforza"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Martial configuration"
    },
    {
        "event_id": "PAVIA-1525",
        "name": "Battle of Pavia",
        "event_type": "war",
        "start_year": 1525, "end_year": 1525,
        "location": "Italy",
        "actors": ["Francis I", "Charles V", "Emperor"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Mars prominent - capture of king"
    },
    {
        "event_id": "ST-DENIS-1567",
        "name": "Tomb of St. Denis Plundered",
        "event_type": "revolution",
        "start_year": 1567, "end_year": 1567,
        "location": "France",
        "actors": ["Charles IX"],
        "period_sources": ["L'Estoile Mémoires-Journaux 1567"],
        "astrology_notes": "Religious conflict"
    },
    {
        "event_id": "DAY_OF_THE_BARRIERS-1588",
        "name": "Day of the Barriers",
        "event_type": "revolution",
        "start_year": 1588, "end_year": 1588,
        "location": "France",
        "actors": ["Henry III", "Duke of Guise"],
        "period_sources": ["L'Estoile Mémoires-Journaux 1588"],
        "astrology_notes": "Saturn-Jupiter tensions"
    },
    {
        "event_id": "POITIERS-1356",
        "name": "Battle of Poitiers",
        "event_type": "war",
        "start_year": 1356, "end_year": 1356,
        "location": "France",
        "actors": ["John II", "Edward the Black Prince"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "Martial defeat"
    },
    {
        "event_id": "CRECY-1346",
        "name": "Battle of Crecy",
        "event_type": "war",
        "start_year": 1346, "end_year": 1346,
        "location": "France",
        "actors": ["Philip VI", "Edward III"],
        "period_sources": ["Froissart Chroniques 1480s"],
        "astrology_notes": "English victory - longbow"
    },
]

# === CYCLES ===

CYCLES = [
    {
        "cycle_id": "rise-fall-empire",
        "name": "Rise and Fall of Empires",
        "event_types": ["war", "revolution", "economic_stress"],
        "typical_duration_years": 50
    },
    {
        "cycle_id": "religious-conflict-cycle",
        "name": "Religious Conflict Cycle",
        "event_types": ["religious_schism", "war", "revolution"],
        "typical_duration_years": 30
    },
    {
        "cycle_id": "plague-famine-war",
        "name": "Plague-Famine-War Triangle",
        "event_types": ["famine", "plague", "war"],
        "typical_duration_years": 20
    },
    {
        "cycle_id": "political-assassination",
        "name": "Political Assassination Sequence",
        "event_types": ["assassination", "revolution", "war"],
        "typical_duration_years": 10
    },
]

def main():
    print("=" * 60)
    print("NOSTRADAMUS PATTERN ENGINE")
    print("=" * 60)

    # Load quatrains
    with open("nostradamus/data/processed/quatrains_bilingual.json", 'r') as f:
        quatrains = json.load(f)
    print(f"\nLoaded {len(quatrains)} quatrains")

    # Load previous analysis
    with open("nostradamus/data/processed/quatrains_analyzed.json", 'r') as f:
        analyzed = json.load(f)

    # Build knowledge graph
    print("\nBuilding knowledge graph...")
    events_for_kg = []
    for e in HISTORICAL_EVENTS:
        events_for_kg.append({
            "event_id": e["event_id"],
            "name": e["name"],
            "event_type": e["event_type"],
            "start_year": e["start_year"],
            "end_year": e.get("end_year"),
            "location": e["location"],
            "actors": e["actors"],
            "period_sources": e["period_sources"],
            "related_events": e.get("related_events", []),
            "astrology_notes": e.get("astrology_notes")
        })

    kg = build_knowledge_graph(events_for_kg)
    print(f"  {len(kg.events)} events loaded")
    print(f"  {len(kg.cycles)} cycles defined")

    # Initialize pattern engine
    engine = PatternEngine(kg)

    # Run pattern analysis
    print("\nRunning pattern analysis...")
    all_matches = []
    symbol_stats = {"lion": 0, "aigle": 0, "serpent": 0, "corbeau": 0, "loup": 0}
    event_type_counts = {}

    for i, q in enumerate(quatrains):
        if i % 100 == 0:
            print(f"  Progress: {i}/{len(quatrains)}")

        # Get previous analysis data
        qid = f"C{q['century']}-Q{q['quatrain']}"
        prev = next((a for a in analyzed if a["id"] == qid), None)

        # Extract schema
        astro = infer_astrological_config(q["french"])
        schema = engine.extract_schema(q, astro)

        # Count symbols
        for sym in schema.symbols:
            if sym in symbol_stats:
                symbol_stats[sym] += 1

        # Count event types
        if schema.event_type.value != "unknown":
            event_type_counts[schema.event_type.value] = event_type_counts.get(schema.event_type.value, 0) + 1

        # Match to events
        matches = engine.match_to_events(schema)
        if matches:
            all_matches.append({
                "quatrain_id": qid,
                "best_match": matches[0].event_name,
                "best_score": matches[0].match_score,
                "event_type": schema.event_type.value,
                "location": schema.location.value,
                "planetary": schema.planetary_config or "none",
                "symbols": schema.symbols,
                "cycles": matches[0].cycle_membership
            })

    # Save results
    output = "nostradamus/data/processed/pattern_analysis.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump({
            "matches": all_matches,
            "statistics": {
                "total_matches": len(all_matches),
                "symbol_frequencies": symbol_stats,
                "event_type_distribution": event_type_counts,
                "cycles_detected": len([m for m in all_matches if m["cycles"]])
            }
        }, f, ensure_ascii=False, indent=2)
    print(f"\nSaved pattern analysis to {output}")

    # Summary
    print("\n" + "=" * 60)
    print("PATTERN ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"\nTotal quatrains analyzed: {len(quatrains)}")
    print(f"Quatrains with event matches: {len(all_matches)}")

    print(f"\nEvent Type Distribution:")
    for et, count in sorted(event_type_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {et}: {count}")

    print(f"\nSymbol Frequencies:")
    for sym, count in sorted(symbol_stats.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {sym}: {count}")

    print(f"\nTop Pattern Matches:")
    for m in sorted(all_matches, key=lambda x: -x["best_score"])[:10]:
        print(f"  {m['quatrain_id']}: {m['best_match']} ({m['best_score']:.3f}) - {m['event_type']}")

if __name__ == "__main__":
    main()
