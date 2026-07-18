"""
Nostradamus Expert System - Integration Layer
Combines all modules into a unified analysis pipeline.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json
from pathlib import Path

from domains.linguistics_module import analyze_text, calculate_ambiguity_index
from domains.astrology_module import infer_astrological_config, PLANET_SYMBOLISM
from domains.history_module import extract_entities, extract_event_type, match_to_events, PERIOD_SOURCES
from pattern_engine import (
    PatternEngine, TemporalKnowledgeGraph, EventType, Region,
    EventSchema, HistoricalEvent, PatternMatch, Cycle,
    build_knowledge_graph, STANDARD_CYCLES
)


class ValidationStatus(Enum):
    VALIDATED = "validated"
    AMBIGUOUS = "ambiguous"
    UNMATCHED = "unmatched"
    ANACHRONISM = "anachronism_detected"


@dataclass
class QuatrainDossier:
    """
    Complete dossier for one quatrain.
    All analysis results in one place.
    """
    quatrain_id: str
    century: int
    quatrain_num: int

    # Text
    french_original: str
    english: str
    french_normalized: str

    # Linguistics
    linguistics: Dict

    # Astrology
    astrology: Dict

    # History / Pattern Matching
    history: Dict
    pattern_match: Optional[PatternMatch]

    # Symbols & Cycles
    symbols: List[str]
    cycle_membership: List[str]

    # Validation
    status: ValidationStatus
    confidence: float
    period_source_alignment: float

    # Metadata
    tier_compliant: bool = True
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "quatrain_id": self.quatrain_id,
            "century": self.century,
            "quatrain_num": self.quatrain_num,
            "french": self.french_original,
            "english": self.english,
            "linguistics": self.linguistics,
            "astrology": {
                "reference_count": self.astrology.get("reference_count", 0),
                "dominant_planet": self.astrology.get("interpretation", {}).get("dominant_planet"),
                "themes": self.astrology.get("interpretation", {}).get("themes", []),
                "augury": self.astrology.get("interpretation", {}).get("augury", "neutral")
            },
            "history": self.history,
            "pattern_match": {
                "event_id": self.pattern_match.event_id if self.pattern_match else None,
                "event_name": self.pattern_match.event_name if self.pattern_match else None,
                "score": self.pattern_match.match_score if self.pattern_match else 0.0,
                "cycles": self.pattern_match.cycle_membership if self.pattern_match else []
            } if self.pattern_match else None,
            "symbols": self.symbols,
            "cycles": self.cycle_membership,
            "status": self.status.value,
            "confidence": self.confidence,
            "period_source_alignment": self.period_source_alignment,
            "tier_compliant": self.tier_compliant,
            "notes": self.notes
        }


class NostradamusEngine:
    """
    Unified Nostradamus analysis engine.
    Combines linguistics, astrology, history, and pattern matching.
    """

    def __init__(self, historical_events: List[Dict]):
        self.kg = build_knowledge_graph(historical_events)
        self.pattern_engine = PatternEngine(self.kg)
        self.dossiers: List[QuatrainDossier] = []

    def analyze_quatrain(self, quatrain: Dict) -> QuatrainDossier:
        """Analyze a single quatrain through all modules."""

        qid = f"C{quatrain['century']}-Q{quatrain['quatrain']}"
        fr = quatrain.get("french", "")
        en = quatrain.get("english", "")

        # 1. Linguistics
        ling = analyze_text(fr, en)

        # 2. Astrology
        astro = infer_astrological_config(fr)

        # 3. History / Entities
        entities = extract_entities(fr)
        event_type_str = extract_event_type(fr)

        # Convert string event type to EventType enum
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            event_type = EventType.UNKNOWN

        # 4. Pattern Schema
        schema = self.pattern_engine.extract_schema(quatrain, astro)

        # 5. Match to events
        pattern_matches = self.pattern_engine.match_to_events(schema)
        best_match = pattern_matches[0] if pattern_matches else None

        # 6. Determine status
        if best_match and best_match.match_score > 0.7:
            status = ValidationStatus.VALIDATED
            confidence = best_match.match_score
        elif best_match and best_match.match_score > 0.4:
            status = ValidationStatus.AMBIGUOUS
            confidence = best_match.match_score
        else:
            status = ValidationStatus.UNMATCHED
            confidence = 0.0

        # 7. Period source alignment (would check against provenance in real implementation)
        period_alignment = 0.8  # Placeholder

        # 8. Build dossier
        dossier = QuatrainDossier(
            quatrain_id=qid,
            century=quatrain["century"],
            quatrain_num=quatrain["quatrain"],
            french_original=fr,
            english=en,
            french_normalized=ling.get("normalized_text", ""),
            linguistics=ling,
            astrology=astro,
            history={
                "entities": entities,
                "event_type": event_type_str,
                "top_match": best_match.event_name if best_match else None,
                "match_score": best_match.match_score if best_match else 0.0,
            },
            pattern_match=best_match,
            symbols=schema.symbols,
            cycle_membership=best_match.cycle_membership if best_match else [],
            status=status,
            confidence=confidence,
            period_source_alignment=period_alignment,
            notes=[]
        )

        return dossier

    def analyze_corpus(self, quatrains: List[Dict]) -> List[QuatrainDossier]:
        """Analyze all quatrains."""

        print(f"Analyzing {len(quatrains)} quatrains...")
        dossiers = []

        for i, q in enumerate(quatrains):
            dossier = self.analyze_quatrain(q)
            dossiers.append(dossier)

            if i % 100 == 0:
                print(f"  Progress: {i}/{len(quatrains)}")

        self.dossiers = dossiers
        return dossiers

    def get_corpus_statistics(self) -> Dict:
        """Generate comprehensive corpus statistics."""

        if not self.dossiers:
            return {}

        # Status counts
        status_counts = {}
        for d in self.dossiers:
            status_counts[d.status.value] = status_counts.get(d.status.value, 0) + 1

        # Planet distribution
        planet_counts = {}
        for d in self.dossiers:
            planet = d.astrology.get("interpretation", {}).get("dominant_planet")
            if planet:
                planet_counts[planet] = planet_counts.get(planet, 0) + 1

        # Event type distribution
        event_type_counts = {}
        for d in self.dossiers:
            et = d.history.get("event_type", "unknown")
            event_type_counts[et] = event_type_counts.get(et, 0) + 1

        # Symbol distribution
        symbol_counts = {}
        for d in self.dossiers:
            for sym in d.symbols:
                symbol_counts[sym] = symbol_counts.get(sym, 0) + 1

        # Cycle membership
        cycle_counts = {}
        for d in self.dossiers:
            for cyc in d.cycle_membership:
                cycle_counts[cyc] = cycle_counts.get(cyc, 0) + 1

        # Ambiguity stats
        ambiguities = [d.linguistics.get("ambiguity_index", 0) for d in self.dossiers]
        avg_ambiguity = sum(ambiguities) / len(ambiguities) if ambiguities else 0

        return {
            "total_quatrains": len(self.dossiers),
            "status_distribution": status_counts,
            "planet_distribution": planet_counts,
            "event_type_distribution": event_type_counts,
            "symbol_distribution": symbol_counts,
            "cycle_membership": cycle_counts,
            "average_ambiguity": round(avg_ambiguity, 3),
            "strong_matches": sum(1 for d in self.dossiers if d.confidence > 0.7),
            "tier_compliant_count": sum(1 for d in self.dossiers if d.tier_compliant)
        }

    def export_dossiers(self, output_path: str) -> None:
        """Export all dossiers to JSON."""
        data = {
            "corpus_statistics": self.get_corpus_statistics(),
            "dossiers": [d.to_dict() for d in self.dossiers]
        }
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Exported {len(self.dossiers)} dossiers to {output_path}")


# === RE EXPORT ===

__all__ = [
    'NostradamusEngine', 'QuatrainDossier', 'ValidationStatus',
    'EventType', 'Region', 'EventSchema', 'HistoricalEvent', 'PatternMatch', 'Cycle',
    'TemporalKnowledgeGraph', 'PatternEngine', 'build_knowledge_graph',
    'STANDARD_CYCLES', 'PERIOD_SOURCES', 'PLANET_SYMBOLISM'
]
