#!/usr/bin/env python3
"""
Run Full Nostradamus Expert System Analysis
Uses integration layer to produce complete dossier for each quatrain.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from integration import NostradamusEngine

# Historical events with period source citations
HISTORICAL_EVENTS = [
    {"event_id": "FRENCH-WARS-1562", "name": "French Wars of Religion", "event_type": "war", "start_year": 1562, "end_year": 1598, "location": "France", "actors": ["Francis II", "Charles IX", "Henry III", "Henry IV", "Catherine de Medici"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "ST-BARTHELEMY-1572", "name": "St. Bartholomew's Day Massacre", "event_type": "war", "start_year": 1572, "end_year": 1572, "location": "France", "actors": ["Charles IX", "Catherine de Medici"], "period_sources": ["de Thou Historia Sui Temporis 1609", "L'Estoile Mémoires-Journaux 1572"]},
    {"event_id": "ARMADA-1588", "name": "Spanish Armada", "event_type": "war", "start_year": 1588, "end_year": 1588, "location": "England", "actors": ["Philip II", "Elizabeth I"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "HENRY-IV-1589", "name": "Henry IV Accession", "event_type": "coronation", "start_year": 1589, "end_year": 1610, "location": "France", "actors": ["Henry IV"], "period_sources": ["L'Estoile Mémoires-Journaux 1589"]},
    {"event_id": "THIRTY-YEARS-1618", "name": "Thirty Years War", "event_type": "war", "start_year": 1618, "end_year": 1648, "location": "Germany", "actors": ["Ferdinand II", "Gustavus Adolphus"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "FRONDE-1648", "name": "Fronde Rebellion", "event_type": "revolution", "start_year": 1648, "end_year": 1653, "location": "France", "actors": ["Louis XIV"], "period_sources": ["L'Estoile Mémoires-Journaux 1648"]},
    {"event_id": "PLAGUE-1720", "name": "Great Plague of Marseille", "event_type": "plague", "start_year": 1720, "end_year": 1721, "location": "France", "actors": ["Louis XV"], "period_sources": ["Belleforest Histoires Tragiques 1570s"]},
    {"event_id": "CONSTANTINOPLE-1453", "name": "Fall of Constantinople", "event_type": "war", "start_year": 1453, "end_year": 1453, "location": "East", "actors": ["Mehmed II", "Constantine XI"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "BLACK-DEATH-1348", "name": "Black Death", "event_type": "plague", "start_year": 1348, "end_year": 1350, "location": "Europe", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "REFORMATION-1517", "name": "Protestant Reformation", "event_type": "religious_schism", "start_year": 1517, "end_year": 1648, "location": "Germany", "actors": ["Martin Luther", "Charles V"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "CHARLES-V-1519", "name": "Charles V Elected Emperor", "event_type": "coronation", "start_year": 1519, "end_year": 1556, "location": "Germany", "actors": ["Charles V", "Francis I"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "NAPLES-1494", "name": "French Invasion of Naples", "event_type": "war", "start_year": 1494, "end_year": 1495, "location": "Italy", "actors": ["Charles VIII"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "PAVIA-1525", "name": "Battle of Pavia", "event_type": "war", "start_year": 1525, "end_year": 1525, "location": "Italy", "actors": ["Francis I", "Charles V"], "period_sources": ["Froissart Chroniques 1480s"]},
]

def main():
    print("=" * 70)
    print("NOSTRADAMUS EXPERT SYSTEM - FULL ANALYSIS")
    print("=" * 70)

    # Load quatrains
    quatrain_path = "nostradamus/data/processed/quatrains_bilingual.json"
    with open(quatrain_path, 'r', encoding='utf-8') as f:
        quatrains = json.load(f)
    print(f"\nLoaded {len(quatrains)} quatrains")

    # Initialize engine
    print("\nInitializing Nostradamus Engine...")
    engine = NostradamusEngine(HISTORICAL_EVENTS)

    # Analyze all quatrains
    print("\nAnalyzing corpus...")
    dossiers = engine.analyze_corpus(quatrains)

    # Statistics
    stats = engine.get_corpus_statistics()

    print("\n" + "=" * 70)
    print("CORPUS STATISTICS")
    print("=" * 70)
    print(f"\nTotal Quatrains: {stats['total_quatrains']}")
    print(f"\nValidation Status:")
    for status, count in stats['status_distribution'].items():
        print(f"  {status}: {count}")
    print(f"\nAstrology - Dominant Planets:")
    for planet, count in sorted(stats['planet_distribution'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {planet}: {count}")
    print(f"\nEvent Types:")
    for et, count in sorted(stats['event_type_distribution'].items(), key=lambda x: -x[1])[:8]:
        print(f"  {et}: {count}")
    print(f"\nSymbols:")
    for sym, count in sorted(stats['symbol_distribution'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {sym}: {count}")
    print(f"\nCycles:")
    for cyc, count in sorted(stats['cycle_membership'].items(), key=lambda x: -x[1]):
        print(f"  {cyc}: {count}")
    print(f"\nAverage Ambiguity Index: {stats['average_ambiguity']}")
    print(f"Strong Matches (score >0.7): {stats['strong_matches']}")

    # Export dossiers
    output_path = "nostradamus/data/processed/nostradamus_dossiers.json"
    engine.export_dossiers(output_path)

    # Show sample dossiers
    print("\n" + "=" * 70)
    print("SAMPLE DOSSIERS")
    print("=" * 70)

    for d in dossiers[:5]:
        print(f"\n{d.quatrain_id}:")
        print(f"  FR: {d.french_original[:60]}...")
        print(f"  Status: {d.status.value} (confidence: {d.confidence:.3f})")
        print(f"  Planet: {d.astrology.get('interpretation', {}).get('dominant_planet', 'none')}")
        print(f"  Event Type: {d.history.get('event_type', 'unknown')}")
        print(f"  Best Match: {d.history.get('top_match', 'none')}")
        print(f"  Symbols: {d.symbols}")
        print(f"  Cycles: {d.cycle_membership}")

    # Strong matches detail
    print("\n" + "=" * 70)
    print("STRONGEST PATTERN MATCHES")
    print("=" * 70)
    strong = [d for d in dossiers if d.confidence > 0.6]
    strong.sort(key=lambda x: -x.confidence)
    for d in strong[:15]:
        print(f"\n{d.quatrain_id}: {d.history.get('top_match', 'N/A')}")
        print(f"  Score: {d.confidence:.3f} | Type: {d.history.get('event_type')} | Planet: {d.astrology.get('interpretation', {}).get('dominant_planet', 'N/A')}")
        print(f"  FR: {d.french_original[:70]}...")

if __name__ == "__main__":
    main()
