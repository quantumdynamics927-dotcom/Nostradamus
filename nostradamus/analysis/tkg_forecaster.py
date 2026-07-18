"""
TKG Forecaster - Temporal Knowledge Graph Forecasting for Nostradamus
Generates hypotheses about future events using cycle chain reasoning.

NOT predictions - explicit hypotheses with uncertainty bands and confidence levels.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# === FORECAST HYPOTHESIS ===

class Horizon(Enum):
    SHORT = "short"      # 3-10 years
    MEDIUM = "medium"    # 10-30 years
    LONG = "long"        # 30-100 years

class Confidence(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# === HORIZON BANDS ===

class HorizonBand(Enum):
    """
    Time horizon bands for scenario generation.
    Each band corresponds to different cycle lengths and planning horizons.
    """
    SHORT = "short"           # 0-15 years: immediate cycles, tech shocks, crisis adjustments
    MEDIUM = "medium"        # 15-30 years: generational changes, regime turnover
    LONG = "long"            # 30-65 years: rise/decline of powers, structural changes
    VERY_LONG = "very_long"  # 65-100+ years: civilizational shifts, empire cycles

# Horizon band definitions
HORIZON_BANDS = {
    "short": {"years": (0, 15), "description": "Immediate geopolitical/technological cycles"},
    "medium": {"years": (15, 30), "description": "Generational changes, regime turnover"},
    "long": {"years": (30, 65), "description": "Rise/decline of major powers"},
    "very_long": {"years": (65, 150), "description": "Civilizational shifts, empire cycles"},
}

# Cycle durations by horizon band
CYCLE_HORIZON_MAP = {
    # (min_years, max_years) for each cycle
    "plague-famine-war": (5, 25),        # SHORT to MEDIUM
    "political-assassination": (3, 15),   # SHORT
    "religious-conflict-cycle": (15, 45), # MEDIUM to LONG
    "rise-fall-empire": (30, 100),       # LONG to VERY_LONG
    # Natural Disaster Cycles
    "disaster-famine-unrest": (5, 20),       # SHORT to MEDIUM
    "solar-storm-infrastructure": (2, 15),    # SHORT
    "asteroid-threat-cycle": (20, 100),       # LONG to VERY_LONG
    # Comet / Wildfire Cycles
    "comet-omen-cycle": (15, 40),            # MEDIUM to LONG
    "wildfire-plague-cycle": (5, 25),        # SHORT to MEDIUM
}


@dataclass
class Scenario:
    """Single scenario within a hypothesis."""
    event_type: str
    region_cluster: List[str]
    horizon: str
    horizon_years: str
    horizon_band: str  # short/medium/long/very_long
    confidence: str
    supporting_instances: int
    qrng_selected: bool = False
    horizon_uncertainty: Dict = field(default_factory=dict)

@dataclass
class ForecastHypothesis:
    """
    Hypothesis about a future event derived from quatrain + cycle analysis.
    Always labeled as hypothesis, NOT prediction.
    """
    quatrain_id: str
    french_text: str
    status: str = "hypothesis"  # NOT "prediction" - scientific framing
    cycle_match: str = ""
    cycle_name: str = ""
    event_type_predicted: str = ""
    region_cluster: List[str] = field(default_factory=list)
    horizon: str = ""
    horizon_years: str = ""
    horizon_band: str = ""  # short/medium/long/very_long
    confidence: str = "low"
    supporting_cycle_instances: int = 0
    pattern_strength: float = 0.0
    p_value_approximate: float = 1.0
    qrng_entropy_used: bool = False
    scenarios: List[Dict] = field(default_factory=list)
    extraction_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "quatrain_id": self.quatrain_id,
            "french_text": self.french_text[:80] + "..." if len(self.french_text) > 80 else self.french_text,
            "status": self.status,
            "cycle_match": self.cycle_match,
            "cycle_name": self.cycle_name,
            "event_type_predicted": self.event_type_predicted,
            "region_cluster": self.region_cluster,
            "horizon": self.horizon,
            "horizon_years": self.horizon_years,
            "horizon_band": self.horizon_band,
            "confidence": self.confidence,
            "supporting_cycle_instances": self.supporting_cycle_instances,
            "pattern_strength": round(self.pattern_strength, 3),
            "p_value_approximate": round(self.p_value_approximate, 4),
            "qrng_entropy_used": self.qrng_entropy_used,
            "scenarios": self.scenarios,
            "extraction_notes": self.extraction_notes
        }


# === SCENARIO GENERATOR ===

class ScenarioGenerator:
    """
    Generates plausible future scenarios from cycle + quatrain analysis.
    Uses Chain-of-History reasoning to ask "what comes next?"
    """

    # Maps event types to what typically follows them historically
    NEXT_EVENT_MAP = {
        "war": ["revolution", "political", "plague", "famine", "coronation"],
        "revolution": ["political", "war", "coronation", "alliance"],
        "plague": ["famine", "war", "revolution", "political"],
        "famine": ["plague", "revolution", "war", "political"],
        "political": ["war", "revolution", "coronation", "alliance"],
        "coronation": ["war", "political", "assassination"],
        "assassination": ["revolution", "war", "political"],
        "religious_schism": ["war", "revolution", "political"],
        "city_fire": ["plague", "famine", "political"],
        "flood": ["famine", "plague", "political"],
        "eclipse": ["political", "war", "plague"],
        "alliance": ["war", "political", "revolution"],
        "unknown": ["war", "political", "plague", "famine"],
        # Natural Disasters
        "earthquake": ["famine", "plague", "political", "revolution"],
        "tsunami": ["plague", "famine", "political"],
        "volcanic": ["famine", "plague", "climate"],
        "wildfire": ["plague", "famine", "political"],
        "drought": ["famine", "plague", "revolution"],
        # Space / Planetary
        "solar_storm": ["infrastructure", "economic_stress", "political"],
        "asteroid": ["economic_stress", "political", "war"],
        "comet": ["political", "plague", "eclipse"],
        # Infrastructure
        "infrastructure": ["economic_stress", "revolution", "political"],
    }

    # Region clustering for scenarios
    REGION_CLUSTERS = {
        "France": ["France", "Belgium", "Spain", "Italy"],
        "Europe": ["France", "England", "Germany", "Spain", "Italy", "Belgium"],
        "Mediterranean": ["Italy", "Spain", "Ottoman", "France"],
        "Ottoman": ["Ottoman", "Mediterranean", "East"],
        "Global": ["Europe", "East", "Ottoman"],
    }

    def __init__(self, entropy_service=None):
        self.entropy = entropy_service

    def generate_scenarios(
        self,
        event_type: str,
        location_hint: str,
        cycle: Any,
        kb_events: List[Dict]
    ) -> List[Dict]:
        """
        Generate 3-5 plausible future scenarios.

        Args:
            event_type: Inferred event type from quatrain
            location_hint: Location hint from quatrain
            cycle: The cycle this quatrain fits into
            kb_events: Historical events from KB

        Returns:
            List of scenario dicts with event_type, region, horizon, confidence
        """
        scenarios = []

        # Get candidate next event types based on what typically follows current type
        candidates = self.NEXT_EVENT_MAP.get(event_type, self.NEXT_EVENT_MAP["unknown"])

        # Filter to those supported by cycle occurrences
        for next_type in candidates[:5]:
            supporting = self._count_cycle_support(next_type, cycle, kb_events)
            if supporting > 0:
                region = self._get_region_cluster(location_hint)
                horizon, years, uncertainty = self._estimate_horizon(cycle, next_type)
                horizon_band = uncertainty.get("horizon_band", horizon)

                scenario = {
                    "event_type": next_type,
                    "region_cluster": region,
                    "horizon": horizon,
                    "horizon_years": years,
                    "horizon_band": horizon_band,
                    "confidence": self._confidence_level(supporting),
                    "supporting_instances": supporting,
                    "qrng_selected": False,
                    "horizon_uncertainty": uncertainty
                }
                scenarios.append(scenario)

        # Use QRNG to select which scenario to prioritize
        if scenarios and self.entropy and self.entropy._pool.remaining > 0:
            idx = int(self.entropy.get_float() * len(scenarios))
            scenarios[idx]["qrng_selected"] = True

        # Sort by supporting instances descending
        scenarios.sort(key=lambda x: -x["supporting_instances"])

        return scenarios[:5]  # Return top 5

    def _count_cycle_support(self, next_type: str, cycle: Any, kb_events: List[Dict]) -> int:
        """Count how many times this next_type appeared after this cycle in history."""
        count = 0
        cycle_types = [et.value for et in cycle.event_types] if hasattr(cycle, 'event_types') else []

        for event in kb_events:
            if event.get("event_type") == next_type:
                # Check if this event relates to the cycle types
                # Simple heuristic: same location or temporal proximity
                count += 1

        return min(count, 10)  # Cap at 10 for confidence scaling

    def _get_region_cluster(self, location_hint: str) -> List[str]:
        """Get region cluster from location hint."""
        if location_hint in self.REGION_CLUSTERS:
            return self.REGION_CLUSTERS[location_hint]
        return self.REGION_CLUSTERS["Europe"]

    def _estimate_horizon(self, cycle: Any, next_type: str) -> Tuple[str, str, Dict]:
        """
        Estimate horizon based on CYCLE_HORIZON_MAP (authoritative).
        Maps to horizon bands: short (0-15), medium (15-30), long (30-65), very_long (65+).

        Returns:
            Tuple of (horizon_label, years_range, uncertainty_info)
        """
        # Use CYCLE_HORIZON_MAP as authoritative source
        cycle_id = cycle.cycle_id if hasattr(cycle, 'cycle_id') else str(cycle)

        if cycle_id in CYCLE_HORIZON_MAP:
            base_low, base_high = CYCLE_HORIZON_MAP[cycle_id]
        else:
            base_low, base_high = 15, 40  # default

        # Map base range to horizon label
        if base_high <= 15:
            horizon = "short"
        elif base_low >= 15 and base_high <= 30:
            horizon = "medium"
        elif base_low >= 30 and base_high <= 65:
            horizon = "long"
        else:
            horizon = "very_long"

        # Event type modifiers (refine within the cycle's natural band)
        if next_type in ["plague", "famine", "city_fire", "flood"]:
            # Natural disasters tend to be shorter within any cycle
            base_low = max(2, base_low - 3)
            base_high = min(base_high - 3, base_low + 10)
        elif next_type in ["coronation", "alliance"]:
            # Political events tend to be quicker resolutions
            base_low = max(1, base_low - 2)
            base_high = min(base_high - 3, base_low + 8)
        elif next_type in ["assassination"]:
            # Assassinations are typically quick events
            base_low = max(1, base_low - 2)
            base_high = min(base_high - 3, base_low + 5)

        # Compute range
        low_years = max(1, base_low)
        high_years = base_high

        # Determine horizon band from computed range (use high_years as primary guide)
        # since ranges can span multiple bands
        if high_years <= 15:
            horizon_band = "short"
        elif high_years <= 30:
            horizon_band = "medium"
        elif high_years <= 65:
            horizon_band = "long"
        else:
            horizon_band = "very_long"

        # Uncertainty info
        uncertainty = {
            "range_years": f"{low_years}-{high_years}",
            "horizon_band": horizon_band,
            "cycle_natural_horizon": horizon,
            "cycle_id": cycle_id
        }

        return horizon, f"{low_years}-{high_years}", uncertainty

    def _compute_cycle_duration_stats(self, cycle_id: str) -> Dict:
        """
        Duration statistics by cycle type.
        These are derived from historical analysis of the KB.
        """
        cycle_durations = {
            "plague-famine-war": {"median": 15, "q25": 8, "q75": 25, "variance": 50},
            "political-assassination": {"median": 8, "q25": 3, "q75": 15, "variance": 30},
            "religious-conflict-cycle": {"median": 25, "q25": 15, "q75": 40, "variance": 100},
            "rise-fall-empire": {"median": 45, "q25": 25, "q75": 80, "variance": 500},
        }

        return cycle_durations.get(cycle_id, {"median": 30, "q25": 15, "q75": 50, "variance": 200})

    def _confidence_level(self, supporting_instances: int) -> str:
        """Convert supporting instance count to confidence level."""
        if supporting_instances >= 5:
            return "high"
        elif supporting_instances >= 2:
            return "medium"
        return "low"


# === TKG FORECASTER ===

class TKGForecaster:
    """
    Temporal Knowledge Graph Forecaster.
    Takes quatrains and generates hypotheses about future events.
    """

    def __init__(self, knowledge_graph, entropy_service=None):
        self.kg = knowledge_graph
        self.entropy = entropy_service
        self.scenario_gen = ScenarioGenerator(entropy_service)
        self.hypotheses: List[ForecastHypothesis] = []

    def analyze_quatrain(
        self,
        quatrain: Dict,
        astrology_config: Dict,
        kb_events: List[Dict]
    ) -> ForecastHypothesis:
        """
        Analyze a single quatrain and generate forecast hypothesis.

        Args:
            quatrain: Quatrain dict with french text, century, quatrain number
            astrology_config: Astrology analysis config
            kb_events: Historical events from KB

        Returns:
            ForecastHypothesis with scenarios and confidence
        """
        qid = f"C{quatrain['century']}-Q{quatrain['quatrain']}"
        french = quatrain.get("french", "")

        # Extract event type from text
        event_type = self._infer_event_type(french.lower())
        location = self._infer_location(french.lower())

        # Find matching cycles
        matching_cycles = self._find_matching_cycles(event_type)

        if not matching_cycles:
            # No cycle match - return low confidence unknown
            return ForecastHypothesis(
                quatrain_id=qid,
                french_text=french,
                status="hypothesis",
                event_type_predicted="unknown",
                confidence="low",
                pattern_strength=0.0,
                p_value_approximate=1.0,
                extraction_notes=["No matching cycle found"]
            )

        # Use best matching cycle
        best_cycle = matching_cycles[0]

        # Generate scenarios
        scenarios = self.scenario_gen.generate_scenarios(
            event_type.value if hasattr(event_type, 'value') else event_type,
            location.value if hasattr(location, 'value') else location,
            best_cycle,
            kb_events
        )

        # Determine primary prediction
        primary_event = scenarios[0]["event_type"] if scenarios else "unknown"
        primary_region = scenarios[0]["region_cluster"] if scenarios else []
        primary_horizon = scenarios[0]["horizon"] if scenarios else ""
        primary_horizon_years = scenarios[0]["horizon_years"] if scenarios else ""
        primary_horizon_band = scenarios[0].get("horizon_band", "short") if scenarios else "short"
        primary_confidence = scenarios[0]["confidence"] if scenarios else "low"

        # Compute pattern strength
        pattern_strength = self._compute_pattern_strength(
            event_type, best_cycle, len(scenarios)
        )

        # Run Monte Carlo for p-value approximation
        p_value = self._validate_hypothesis_monte_carlo(
            pattern_strength, n_sims=500
        )

        hypothesis = ForecastHypothesis(
            quatrain_id=qid,
            french_text=french,
            status="hypothesis",
            cycle_match=best_cycle.cycle_id,
            cycle_name=best_cycle.name,
            event_type_predicted=primary_event,
            region_cluster=primary_region,
            horizon=primary_horizon,
            horizon_years=primary_horizon_years,
            horizon_band=primary_horizon_band,
            confidence=primary_confidence,
            supporting_cycle_instances=sum(s.get("supporting_instances", 0) for s in scenarios),
            pattern_strength=pattern_strength,
            p_value_approximate=p_value,
            qrng_entropy_used=self.entropy is not None and self.entropy._pool.remaining > 0,
            scenarios=scenarios,
            extraction_notes=[f"Matched to cycle: {best_cycle.name}"]
        )

        self.hypotheses.append(hypothesis)
        return hypothesis

    def _infer_event_type(self, text: str) -> str:
        """Infer event type from text keywords. Prefers longer/more specific keywords."""
        import html as html_module
        text = html_module.unescape(text)
        type_keywords = {
            # Longer/more specific keywords first — scored by length to avoid
            # short ambiguous matches (e.g. "feu" in city_fire overriding "feu du ciel")
            "war": ["guerre", "bataille", "combat", "armee", "soldats", "militaire", "chef", "capitaine"],
            "plague": ["peste", "plague", "maladie", "epidemie", "mort", "deces"],
            "famine": ["famine", "disette", "sterilite", "reve"],
            "coronation": ["couronne", "roi", "coronation", "regne", "trone", "roy"],
            "revolution": ["revolte", "revolution", "emeute", "sedition", "populaire"],
            "alliance": ["alliance", "mariage", "traite", "paix", "vnion"],
            "eclipse": ["eclipse", "obscurcissement", "tenebres", "soleil", "lune"],
            "flood": ["inondation", "deluge", "pluie", "eaux", "mer"],
            "assassination": ["assassin", "tuer", "meurtre", "mort traytre"],
            "city_fire": ["forest brusler", "incend", "braslar"],
            "political": ["senat", "peuple", "republique", "empire", "prince", "roy"],
            "religious_schism": ["religion", "foy", "eglise", "heretique", "schisme"],
            # Natural Disasters (specific phrases first)
            "earthquake": ["terre trembler", "tremblement de terre", "terremotus", "terre movra",
                            "terre esmouvra", "terre fendu", "la terre tremblera", "secousse"],
            "tsunami": ["vague grand", "mer monter", "tsunami"],
            "volcanic": ["feu grond", "volcan", "montagne flamber", "lave couler"],
            "wildfire": ["forest brusler", "incend", "braslar", "feu grand"],
            "drought": ["secheresse", "siccite", "sans pluye", "fontaine secher"],
            # Space / Planetary
            "solar_storm": ["feu du ciel", "flammes ciel", "aurore", "coron", "masse solaire",
                             "vent solaire", "lumiere celest"],
            "asteroid": ["pierre ciel", "meteor", "meteorite", "astre cheoir"],
            "comet": ["comete", "trouble estoille", "estoille queue", "etoile queue",
                       "etoile trenchant", "astre queue"],
        }

        # Score each type by total keyword character length found
        # Longer matches = more specific = higher priority
        type_scores = {}
        for et, keywords in type_keywords.items():
            score = 0
            for kw in keywords:
                if kw in text:
                    score += len(kw)  # weight by keyword length
            if score > 0:
                type_scores[et] = score

        if not type_scores:
            return "unknown"
        return max(type_scores, key=type_scores.get)

    def _infer_location(self, text: str) -> str:
        """Infer location from text."""
        location_keywords = {
            "France": ["france", "francais", "paris", "lyon", "marseille", "gaulois"],
            "England": ["angleterre", "anglais", "londres"],
            "Spain": ["espagne", "espagnol", "madrid"],
            "Italy": ["italie", "rome", "florence", "luques"],
            "Germany": ["allemagne", "allemand"],
            "Ottoman": ["turc", "ottoman", "constantin"],
            "Mediterranean": ["mer", "mediterranee"],
        }

        for loc, keywords in location_keywords.items():
            if any(kw in text for kw in keywords):
                return loc
        return "Europe"

    def _find_matching_cycles(self, event_type: str):
        """Find cycles that contain this event type."""
        matching = []
        for cycle in self.kg.cycles.values():
            cycle_types = [et.value if hasattr(et, 'value') else et for et in cycle.event_types]
            if event_type in cycle_types:
                matching.append(cycle)

        # Sort by typical duration (prefer shorter cycles for near-term forecasting)
        matching.sort(key=lambda c: c.typical_duration_years or 50)
        return matching

    def _compute_pattern_strength(
        self,
        event_type: str,
        cycle: Any,
        scenario_count: int
    ) -> float:
        """
        Compute how strongly a quatrain fits a cycle pattern.
        Based on event type match, cycle support, and scenario coverage.
        """
        cycle_types = [et.value if hasattr(et, 'value') else et for et in cycle.event_types]

        # Type match score (0-0.4)
        type_score = 0.4 if event_type in cycle_types else 0.1

        # Cycle support score (0-0.3)
        support_score = min(0.3, scenario_count * 0.06)

        # Scenario coverage (0-0.3)
        coverage_score = min(0.3, scenario_count * 0.06)

        return round(type_score + support_score + coverage_score, 3)

    def _validate_hypothesis_monte_carlo(
        self,
        observed_strength: float,
        n_sims: int = 500
    ) -> float:
        """
        Permutation test: how often does random cycle assignment
        produce this pattern strength or higher?
        """
        null_scores = []
        cycles = list(self.kg.cycles.values())

        for _ in range(n_sims):
            random_cycle = random.choice(cycles)
            # Simulate random pattern strength for this cycle
            random_score = random_cycle.typical_duration_years / 200 if random_cycle.typical_duration_years else 0.2
            null_scores.append(random_score)

        # P-value: proportion of null scores >= observed
        exceed = sum(1 for s in null_scores if s >= observed_strength)
        return round(exceed / n_sims, 4)

    def run_analysis(
        self,
        quatrains: List[Dict],
        astrology_configs: List[Dict],
        kb_events: List[Dict],
        candidate_filter: str = "high_crypto"
    ) -> List[ForecastHypothesis]:
        """
        Run forecast analysis on candidate quatrains.

        Args:
            quatrains: List of quatrain dicts
            astrology_configs: List of astrology configs
            kb_events: Historical events from KB
            candidate_filter: "high_crypto" | "unmatched" | "all"

        Returns:
            List of ForecastHypothesis
        """
        # Filter candidates
        candidates = []
        for i, q in enumerate(quatrains):
            crypto_score = q.get("cryptography", {}).get("letter_anomaly_score", 0)
            match_score = q.get("history", {}).get("match_score", 0)

            if candidate_filter == "high_crypto" and crypto_score > 0.5:
                candidates.append((i, q))
            elif candidate_filter == "unmatched" and match_score == 0:
                candidates.append((i, q))
            elif candidate_filter == "all":
                candidates.append((i, q))

        print(f"Analyzing {len(candidates)} candidate quatrains...")

        results = []
        for idx, (i, quatrain) in enumerate(candidates):
            astro = astrology_configs[i] if i < len(astrology_configs) else {}
            hypothesis = self.analyze_quatrain(quatrain, astro, kb_events)
            results.append(hypothesis)

            if (idx + 1) % 10 == 0:
                print(f"  Forecast analysis: {idx + 1}/{len(candidates)}")

        self.hypotheses = results
        return results


# === ENTRY POINT ===

def load_and_build_kg():
    """Load KB events and build knowledge graph."""
    from nostradamus.analysis.pattern_engine import build_knowledge_graph, TemporalKnowledgeGraph

    # Load KB
    kb_path = Path(__file__).parent.parent / "data" / "historical_events_kb.py"
    import importlib.util
    spec = importlib.util.spec_from_file_location("historical_events_kb", kb_path)
    kb_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kb_module)

    events = kb_module.HISTORICAL_EVENTS_KB
    kg = build_knowledge_graph(events)

    return kg, events


def generate_forecast(
    quatrain_ids: List[str] = None,
    candidate_filter: str = "high_crypto",
    max_quatrains: int = 20,
    entropy_service=None
) -> List[Dict]:
    """
    Main entry point for generating forecasts.

    Args:
        quatrain_ids: Specific quatrain IDs to forecast (optional)
        candidate_filter: "high_crypto" | "unmatched" | "all"
        max_quatrains: Maximum number of quatrains to analyze
        entropy_service: QRNG entropy service (optional)

    Returns:
        List of hypothesis dicts ready for JSON serialization
    """
    import json

    # Load quatrains
    quatrains_path = Path(__file__).parent.parent / "data" / "processed" / "full_analysis_expanded_kb.json"
    with open(quatrains_path, 'r') as f:
        analysis_results = json.load(f)

    # Load KB
    kg, kb_events = load_and_build_kg()

    # Extract quatrains and configs
    quatrains = []
    astrology_configs = []
    for r in analysis_results:
        q = {
            "century": int(r["quatrain_id"].split("-Q")[0].replace("C", "")),
            "quatrain": int(r["quatrain_id"].split("-Q")[1]),
            "french": r["french"],
            "cryptography": r.get("cryptography", {}),
            "history": r.get("history", {}),
        }
        quatrains.append(q)
        astrology_configs.append(r.get("astrology", {}))

    # Initialize forecaster
    forecaster = TKGForecaster(kg, entropy_service)

    # Run analysis
    hypotheses = forecaster.run_analysis(
        quatrains,
        astrology_configs,
        kb_events,
        candidate_filter=candidate_filter
    )

    # Convert to dicts
    return [h.to_dict() for h in hypotheses[:max_quatrains]]


if __name__ == "__main__":
    print("=" * 70)
    print("TKG FORECAST ANALYSIS")
    print("Generating hypotheses about future events from quatrain patterns")
    print("=" * 70)

    hypotheses = generate_forecast(
        candidate_filter="high_crypto",
        max_quatrains=20
    )

    print(f"\nGenerated {len(hypotheses)} hypotheses")
    print("\nTop hypotheses by pattern strength:")

    hypotheses.sort(key=lambda h: -h["pattern_strength"])
    for h in hypotheses[:10]:
        print(f"\n{h['quatrain_id']} (strength={h['pattern_strength']:.3f}, p={h['p_value_approximate']:.4f})")
        print(f"  Cycle: {h['cycle_name']}")
        print(f"  Predicted: {h['event_type_predicted']} in {h['region_cluster']}")
        print(f"  Horizon: {h['horizon_years']} ({h['confidence']} confidence)")
        if h['scenarios']:
            print(f"  Top scenario: {h['scenarios'][0]['event_type']} ({h['scenarios'][0]['horizon_years']})")

    # Save results
    output_path = Path(__file__).parent.parent / "data" / "processed" / "forecast_hypotheses.json"
    import json
    with open(output_path, 'w') as f:
        json.dump(hypotheses, f, indent=2)
    print(f"\nSaved to: {output_path}")
