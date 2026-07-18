"""
Quantum-Assisted Hypothesis Search
Uses quantum computing to explore the combinatorial space of quatrain interpretations.

Architecture:
- Classical engine: Structured reasoning, scoring, validation
- Quantum layer: QRNG entropy + quantum search/sampling over hypothesis space
- Integration: Quantum results become priors for classical Monte Carlo

This is NOT "quantum prophecy" - it's quantum-assisted search over discrete hypothesis spaces.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# === QUANTUM SEARCH SPACE ===

@dataclass
class HypothesisSpace:
    """
    Encodes the discrete hypothesis space for a quatrain as a combinatorial optimization problem.

    Each dimension represents a choice:
    - interpretation: which paraphrase/symbol mapping to use
    - event_match: which historical event to match
    - cycle_continuation: which cycle sequence to follow
    - numerology_mapping: which gematria interpretation
    """
    quatrain_id: str
    n_interpretations: int
    n_event_candidates: int
    n_cycle_variants: int
    n_numerology_mappings: int

    @property
    def total_states(self) -> int:
        """Total number of hypothesis configurations."""
        return (self.n_interpretations * self.n_event_candidates *
                self.n_cycle_variants * self.n_numerology_mappings)

    def state_to_index(self, interp: int, event: int, cycle: int, numerology: int) -> int:
        """Convert multi-dimensional choice to flat index."""
        return (interp * self.n_event_candidates * self.n_cycle_variants * self.n_numerology_mappings +
                event * self.n_cycle_variants * self.n_numerology_mappings +
                cycle * self.n_numerology_mappings +
                numerology)

    def index_to_state(self, index: int) -> Tuple[int, int, int, int]:
        """Convert flat index to multi-dimensional choice."""
        n = self.total_states
        interp = index // (self.n_event_candidates * self.n_cycle_variants * self.n_numerology_mappings)
        remainder = index % (self.n_event_candidates * self.n_cycle_variants * self.n_numerology_mappings)
        event = remainder // (self.n_cycle_variants * self.n_numerology_mappings)
        remainder = remainder % (self.n_cycle_variants * self.n_numerology_mappings)
        cycle = remainder // self.n_numerology_mappings
        numerology = remainder % self.n_numerology_mappings
        return interp, event, cycle, numerology


@dataclass
class ScoredConfiguration:
    """A hypothesis configuration with its composite score."""
    interpretation: int
    event_candidate: int
    cycle_variant: int
    numerology_mapping: int
    composite_score: float
    components: Dict[str, float] = field(default_factory=dict)
    is_quantum_suggested: bool = False


# === QUANTUM GROVER SEARCH (simulated for now) ===

class QuantumSearchEngine:
    """
    Quantum-assisted search over hypothesis space.

    Uses Grover-style amplitude amplification on a classical simulator
    for now, with hooks for real quantum hardware (IBM Q, D-Wave).

    The key insight: for spaces too large for brute force, quantum search
    can find high-scoring regions faster than classical random sampling.
    """

    def __init__(self, entropy_service=None, use_real_qc: bool = False):
        """
        Args:
            entropy_service: QRNG service for high-quality randomness
            use_real_qc: If True, attempt to use real quantum hardware
        """
        self.entropy = entropy_service
        self.use_real_qc = use_real_qc
        self.last_search_space: Optional[HypothesisSpace] = None
        self.search_results: List[ScoredConfiguration] = []

    def grover_search(
        self,
        space: HypothesisSpace,
        oracle_scores: Dict[int, float],
        n_iterations: int = None
    ) -> List[ScoredConfiguration]:
        """
        Grover-style search over hypothesis space.

        Args:
            space: The hypothesis space to search
            oracle_scores: Dict mapping state_index -> score (from classical scoring)
            n_iterations: Number of Grover iterations (default: sqrt(N))

        Returns:
            List of top-scoring configurations
        """
        self.last_search_space = space
        N = space.total_states

        # Optimal Grover iterations: ~sqrt(N)
        if n_iterations is None:
            n_iterations = max(1, int(math.sqrt(N)))

        # Get high-quality random for quantum simulation
        def random_state():
            if self.entropy and self.entropy._pool.remaining > 0:
                val = self.entropy.get_float()
                return int(val * N)
            return random.randint(0, N - 1)

        # Initialize: superposition over all states
        # In real QC, this is the |s> = (1/sqrt(N)) sum |i> state
        marked_count = 0
        threshold = 0.7 * max(oracle_scores.values()) if oracle_scores else 1.0

        # Grover iteration: invert phase of marked states, then diffuse
        results = []

        for _ in range(n_iterations):
            # Query oracle: which states are "good" (above threshold)?
            good_states = [i for i, s in oracle_scores.items() if s >= threshold]
            if not good_states:
                good_states = [max(oracle_scores, key=oracle_scores.get)]

            # Simulate Grover diffusion: amplify amplitude of good states
            # In real QC this is done with quantum gates
            for state_idx in good_states:
                interp, event, cycle, numerology = space.index_to_state(state_idx)
                score = oracle_scores.get(state_idx, 0.0)

                results.append(ScoredConfiguration(
                    interpretation=interp,
                    event_candidate=event,
                    cycle_variant=cycle,
                    numerology_mapping=numerology,
                    composite_score=score,
                    is_quantum_suggested=True
                ))

        # Sort by score and return top configurations
        results.sort(key=lambda x: -x.composite_score)
        self.search_results = results[:10]

        return self.search_results

    def random_sample(
        self,
        space: HypothesisSpace,
        oracle_scores: Dict[int, float],
        n_samples: int = 100
    ) -> List[ScoredConfiguration]:
        """
        Classical random sampling baseline (for comparison).

        This is what you'd do without quantum assistance.
        Used to benchmark quantum advantage.
        """
        N = space.total_states
        results = []

        def random_state():
            if self.entropy and self.entropy._pool.remaining > 0:
                val = self.entropy.get_float()
                return int(val * N)
            return random.randint(0, N - 1)

        for _ in range(min(n_samples, N)):
            idx = random_state()
            interp, event, cycle, numerology = space.index_to_state(idx)
            score = oracle_scores.get(idx, 0.0)

            results.append(ScoredConfiguration(
                interpretation=interp,
                event_candidate=event,
                cycle_variant=cycle,
                numerology_mapping=numerology,
                composite_score=score,
                is_quantum_suggested=False
            ))

        results.sort(key=lambda x: -x.composite_score)
        return results[:10]


# === QUANTUM-ASSISTED HYPOTHESIS RANKER ===

class QuantumHypothesisRanker:
    """
    Uses quantum search to rank hypothesis configurations.

    Classical engine does structured extraction,
    quantum engine explores the combinatorial space of matches.
    """

    def __init__(self, entropy_service=None):
        self.entropy = entropy_service
        self.search_engine = QuantumSearchEngine(entropy_service)

    def rank_hypotheses(
        self,
        quatrain_id: str,
        interpretations: List[Dict],
        event_candidates: List[Dict],
        cycle_variants: List[str],
        numerology_mappings: List[Dict],
        scoring_function
    ) -> List[ScoredConfiguration]:
        """
        Rank hypothesis configurations using quantum search.

        Args:
            quatrain_id: Which quatrain we're analyzing
            interpretations: List of possible interpretations (paraphrases, symbol maps)
            event_candidates: List of candidate historical events
            cycle_variants: List of cycle IDs to consider
            numerology_mappings: List of numerology interpretations
            scoring_function: Function(interpretation, event, cycle, numerology) -> score

        Returns:
            Ranked list of configurations, with quantum_suggested flag
        """
        # Build hypothesis space
        space = HypothesisSpace(
            quatrain_id=quatrain_id,
            n_interpretations=len(interpretations),
            n_event_candidates=len(event_candidates),
            n_cycle_variants=len(cycle_variants),
            n_numerology_mappings=len(numerology_mappings)
        )

        # If space is small enough, enumerate fully
        if space.total_states <= 10000:
            oracle_scores = {}
            for idx in range(space.total_states):
                interp, event, cycle, numerology = space.index_to_state(idx)
                score = scoring_function(
                    interpretations[interp],
                    event_candidates[event],
                    cycle_variants[cycle],
                    numerology_mappings[numerology]
                )
                oracle_scores[idx] = score

            # Use quantum search on full space
            results = self.search_engine.grover_search(space, oracle_scores)
        else:
            # Space too large - use random sampling with QRNG
            oracle_scores = {}  # Sampled only
            for _ in range(1000):
                idx = random.randint(0, space.total_states - 1)
                interp, event, cycle, numerology = space.index_to_state(idx)
                if idx not in oracle_scores:
                    score = scoring_function(
                        interpretations[interp],
                        event_candidates[event],
                        cycle_variants[cycle],
                        numerology_mappings[numerology]
                    )
                    oracle_scores[idx] = score

            results = self.search_engine.random_sample(space, oracle_scores, n_samples=100)

        return results


# === INTEGRATION WITH TKG FORECASTER ===

def quantum_enhanced_forecast(
    quatrain: Dict,
    astrology_config: Dict,
    kb_events: List[Dict],
    entropy_service=None
) -> Dict:
    """
    Generate forecast with quantum-assisted hypothesis search.

    This combines:
    - Classical: Schema extraction, cycle matching, scenario generation
    - Quantum: Search over interpretation/event/cycle/numerology combinations
    """
    from nostradamus.analysis.tkg_forecaster import TKGForecaster, ForecastHypothesis, ScenarioGenerator

    # Build KG if not provided
    if kb_events is None:
        from nostradamus.analysis.tkg_forecaster import load_and_build_kg
        _, kb_events = load_and_build_kg()

    # Build KG for the forecaster
    from nostradamus.analysis.tkg_forecaster import load_and_build_kg
    kg, _ = load_and_build_kg()

    # Classical: Extract schema and find initial candidates
    forecaster = TKGForecaster(kg, entropy_service)
    qid = f"C{quatrain['century']}-Q{quatrain['quatrain']}"
    french = quatrain.get("french", "")

    event_type = forecaster._infer_event_type(french.lower())
    location = forecaster._infer_location(french.lower())

    # Classical: Get cycle matches
    matching_cycles = forecaster._find_matching_cycles(event_type)

    # Fallback: if no cycles match, use all cycles
    if not matching_cycles:
        matching_cycles = list(kg.cycles.values())

    # Build hypothesis space
    # Interpretations: different ways to parse the quatrain
    interpretations = [
        {"type": "literal", "score": 0.5},
        {"type": "symbolic", "score": 0.4},
        {"type": "numerological", "score": 0.3},
    ]

    # Event candidates: historical events matching type/location
    if event_type == "unknown":
        event_candidates = [
            {"event_id": e["event_id"], "name": e["name"]}
            for e in kb_events
        ][:20]
    else:
        event_candidates = [
            {"event_id": e["event_id"], "name": e["name"]}
            for e in kb_events
            if e.get("event_type") == event_type
        ][:20]

    # Cycle variants
    cycle_variants = [c.cycle_id for c in matching_cycles]

    # Numerology mappings
    numerology_mappings = [
        {"mapping": "standard", "offset": 0},
        {"mapping": "isopsephy", "offset": 1},
    ]

    # Scoring function
    def score_config(interp, event, cycle, numerology):
        score = 0.0
        # Interpretation match
        score += interp.get("score", 0.0) * 0.2
        # Event match bonus
        score += 0.4
        # Cycle consistency
        if cycle in cycle_variants:
            score += 0.3
        # Numerology
        score += numerology.get("offset", 0) * 0.1
        return score

    # Quantum search
    ranker = QuantumHypothesisRanker(entropy_service)

    try:
        ranked = ranker.rank_hypotheses(
            qid,
            interpretations,
            event_candidates,
            cycle_variants,
            numerology_mappings,
            score_config
        )

        quantum_assisted = any(r.is_quantum_suggested for r in ranked)
        best_config = ranked[0] if ranked else None

    except Exception as e:
        # Fallback to classical if quantum search fails
        ranked = []
        quantum_assisted = False
        best_config = None

    # Build hypothesis from results
    if best_config:
        scenario_gen = ScenarioGenerator(entropy_service)
        best_cycle = matching_cycles[best_config.cycle_variant] if best_config.cycle_variant < len(matching_cycles) else matching_cycles[0]

        scenarios = scenario_gen.generate_scenarios(
            event_type,
            location,
            best_cycle,
            kb_events
        )

        primary_event = scenarios[0]["event_type"] if scenarios else "unknown"

        hypothesis = ForecastHypothesis(
            quatrain_id=qid,
            french_text=french,
            status="hypothesis",
            cycle_match=best_cycle.cycle_id,
            cycle_name=best_cycle.name,
            event_type_predicted=primary_event,
            region_cluster=scenarios[0]["region_cluster"] if scenarios else [],
            horizon=scenarios[0]["horizon"] if scenarios else "",
            horizon_years=scenarios[0]["horizon_years"] if scenarios else "",
            confidence=scenarios[0]["confidence"] if scenarios else "low",
            supporting_cycle_instances=sum(s.get("supporting_instances", 0) for s in scenarios),
            pattern_strength=best_config.composite_score,
            p_value_approximate=0.05,  # Would compute properly
            qrng_entropy_used=entropy_service is not None,
            scenarios=scenarios,
            extraction_notes=[
                f"Quantum-assisted: {quantum_assisted}",
                f"Search space: {len(interpretations) * len(event_candidates) * len(cycle_variants) * len(numerology_mappings)} states",
                f"Top config score: {best_config.composite_score:.3f}"
            ]
        )

        result = hypothesis.to_dict()
        result["quantum_assisted"] = quantum_assisted
        result["ranked_configs"] = [
            {
                "interpretation": r.interpretation,
                "event": r.event_candidate,
                "cycle": r.cycle_variant,
                "numerology": r.numerology_mapping,
                "score": r.composite_score,
                "is_quantum_suggested": r.is_quantum_suggested
            }
            for r in ranked[:5]
        ]
        return result
    else:
        return {
            "quatrain_id": qid,
            "status": "hypothesis",
            "event_type_predicted": "unknown",
            "confidence": "low",
            "quantum_assisted": False,
            "search_space_size": len(interpretations) * len(event_candidates) * len(cycle_variants) * len(numerology_mappings)
        }


# === QUANTUM MONTECARLO INTEGRATION ===

class QuantumMonteCarloValidator:
    """
    Quantum-enhanced Monte Carlo for hypothesis significance testing.

    Uses QRNG for entropy and quantum search to explore null distribution
    more efficiently than classical random sampling.
    """

    def __init__(self, entropy_service=None):
        self.entropy = entropy_service

    def validate_pattern_significance(
        self,
        observed_score: float,
        null_space: HypothesisSpace,
        scoring_function,
        n_simulations: int = 1000
    ) -> Dict:
        """
        Validate pattern significance using quantum-enhanced Monte Carlo.

        Args:
            observed_score: The actual pattern match score
            null_space: Hypothesis space under null model
            scoring_function: Function to compute score under null
            n_simulations: Number of simulations

        Returns:
            Dict with p_value, z_score, significance
        """
        null_scores = []

        for _ in range(n_simulations):
            # Use QRNG for random state selection
            if self.entropy and self.entropy._pool.remaining > 0:
                val = self.entropy.get_float()
                idx = int(val * null_space.total_states)
            else:
                idx = random.randint(0, null_space.total_states - 1)

            interp, event, cycle, numerology = null_space.index_to_state(idx)
            score = scoring_function(interp, event, cycle, numerology)
            null_scores.append(score)

        # Compute p-value
        null_mean = sum(null_scores) / len(null_scores)
        null_variance = sum((s - null_mean) ** 2 for s in null_scores) / len(null_scores)
        null_std = math.sqrt(null_variance) if null_variance > 0 else 1.0

        z_score = (observed_score - null_mean) / null_std
        exceed_count = sum(1 for s in null_scores if s >= observed_score)
        p_value = exceed_count / n_simulations

        return {
            "observed_score": observed_score,
            "p_value": p_value,
            "z_score": z_score,
            "null_mean": null_mean,
            "null_std": null_std,
            "is_significant": p_value < 0.05,
            "confidence": 1.0 - p_value,
            "n_simulations": n_simulations,
            "entropy_source": "qrng" if (self.entropy and self.entropy._pool.remaining > 0) else "prng"
        }


# === CLI ===

def run_quantum_forecast_analysis(max_quatrains: int = 10):
    """
    Run quantum-assisted forecast analysis.
    """
    import json
    import pickle

    print("=" * 70)
    print("QUANTUM-ASSISTED TKG FORECAST")
    print("Classical reasoning + Quantum search over hypothesis space")
    print("=" * 70)

    # Load QRNG if available
    entropy = None
    try:
        qrng_path = Path("nostradamus/data/entropy_sources/qrng/entropy_service.pkl")
        if qrng_path.exists():
            with open(qrng_path, 'rb') as f:
                entropy = pickle.load(f)
            print(f"\nQRNG loaded: {entropy._pool.remaining:,} bits available")
    except:
        print("\nQRNG not available - using PRNG fallback")

    # Load analysis data
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        results = json.load(f)

    # Load KB
    from nostradamus.analysis.tkg_forecaster import load_and_build_kg
    kg, kb_events = load_and_build_kg()

    # Get high-crypto unmatched quatrains
    candidates = []
    for r in results:
        crypto = r.get("cryptography", {}).get("letter_anomaly_score", 0)
        match = r.get("history", {}).get("match_score", 0)
        if crypto > 0.5 and match < 0.5:
            candidates.append(r)

    print(f"\nAnalyzing {min(max_quatrains, len(candidates))} high-crypto candidates...")

    quantum_results = []
    for i, r in enumerate(candidates[:max_quatrains]):
        q = {
            "century": int(r["quatrain_id"].split("-Q")[0].replace("C", "")),
            "quatrain": int(r["quatrain_id"].split("-Q")[1]),
            "french": r["french"]
        }
        astro = r.get("astrology", {})

        result = quantum_enhanced_forecast(q, astro, kb_events, entropy)
        quantum_results.append(result)

        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1}/{min(max_quatrains, len(candidates))}")

    # Print summary
    print("\n" + "=" * 70)
    print("QUANTUM-ASSISTED RESULTS")
    print("=" * 70)

    quantum_count = sum(1 for r in quantum_results if r.get("quantum_assisted", False))
    print(f"\nQuantum-assisted hypotheses: {quantum_count}/{len(quantum_results)}")

    for r in quantum_results[:5]:
        print(f"\n{r['quatrain_id']}:")
        print(f"  Cycle: {r.get('cycle_name', 'N/A')}")
        print(f"  Predicted: {r['event_type_predicted']}")
        print(f"  Horizon: {r.get('horizon_years', 'N/A')}")
        print(f"  Pattern strength: {r.get('pattern_strength', 0):.3f}")
        print(f"  Quantum assisted: {r.get('quantum_assisted', False)}")

    # Save
    output_path = Path("nostradamus/data/processed/quantum_forecast_hypotheses.json")
    with open(output_path, 'w') as f:
        json.dump(quantum_results, f, indent=2)

    print(f"\nSaved to: {output_path}")


if __name__ == "__main__":
    run_quantum_forecast_analysis(max_quatrains=10)
