#!/usr/bin/env python3
"""
Quantum Hypothesis Search Experiment
Compare classical sampling vs quantum search on 10 quatrains.
Store results in forecast_hypotheses.json for analysis.
"""

import sys
import json
import random
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

try:
    import pickle
    QRNG_AVAILABLE = True
except:
    QRNG_AVAILABLE = False


def main():
    print("=" * 70)
    print("QUANTUM HYPOTHESIS SEARCH EXPERIMENT")
    print("Comparing classical sampling vs quantum search on 10 quatrains")
    print("=" * 70)

    # Load QRNG if available
    entropy = None
    if QRNG_AVAILABLE:
        try:
            qrng_path = Path("nostradamus/data/entropy_sources/qrng/entropy_service.pkl")
            if qrng_path.exists():
                with open(qrng_path, 'rb') as f:
                    entropy = pickle.load(f)
                print(f"\nQRNG loaded: {entropy._pool.remaining:,} bits available")
        except:
            print("\nQRNG not available - using PRNG fallback")

    # Load modules
    from nostradamus.analysis.tkg_forecaster import load_and_build_kg, TKGForecaster
    from nostradamus.analysis.quantum_hypothesis_search import (
        QuantumSearchEngine, HypothesisSpace, ScoredConfiguration
    )

    # Build KG
    kg, kb_events = load_and_build_kg()
    print(f"\nKnowledge graph: {len(kg.events)} events, {len(kg.cycles)} cycles")

    # Load quatrains
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        results = json.load(f)

    # Select 10 candidate quatrains:
    # - Mix of unmatched and weakly matched
    # - Different crypto anomaly levels
    # - Different cycles
    candidates = []

    # High crypto, unmatched
    high_crypto_unmatched = [
        r for r in results
        if r.get("cryptography", {}).get("letter_anomaly_score", 0) > 0.5
        and r.get("history", {}).get("match_score", 0) < 0.3
    ]
    random.seed(42)
    candidates.extend(random.sample(high_crypto_unmatched, min(5, len(high_crypto_unmatched))))

    # Weakly matched but interesting
    weakly_matched = [
        r for r in results
        if 0.3 <= r.get("history", {}).get("match_score", 0) < 0.6
    ]
    candidates.extend(random.sample(weakly_matched, min(3, len(weakly_matched))))

    # Strong pattern match candidates
    strong_pattern = [
        r for r in results
        if r.get("history", {}).get("match_score", 0) >= 0.6
    ]
    candidates.extend(random.sample(strong_pattern, min(2, len(strong_pattern))))

    print(f"\nAnalyzing {len(candidates)} candidate quatrains...")

    # Run analysis on each
    experiment_results = []

    for i, target in enumerate(candidates):
        qid = target["quatrain_id"]
        french = target["french"]
        crypto_score = target.get("cryptography", {}).get("letter_anomaly_score", 0)
        match_score = target.get("history", {}).get("match_score", 0)
        event_type = target.get("history", {}).get("event_type", "unknown")

        print(f"\n{i+1}. {qid} (crypto={crypto_score:.2f}, match={match_score:.2f})")

        # Build quatrain dict
        q = {
            "century": int(qid.split("-Q")[0].replace("C", "")),
            "quatrain": int(qid.split("-Q")[1]),
            "french": french
        }

        # Get forecaster for cycle info
        forecaster = TKGForecaster(kg, entropy)
        et = forecaster._infer_event_type(french.lower())
        loc = forecaster._infer_location(french.lower())
        matching_cycles = forecaster._find_matching_cycles(et)
        if not matching_cycles:
            matching_cycles = list(kg.cycles.values())

        # Build hypothesis space
        interpretations = [
            {"type": "literal", "score": 0.5},
            {"type": "symbolic", "score": 0.4},
            {"type": "numerological", "score": 0.3},
        ]

        event_candidates = [
            {"event_id": e["event_id"], "name": e["name"]}
            for e in kb_events
            if e.get("event_type") == et or et == "unknown"
        ][:20]

        cycle_variants = [c.cycle_id for c in matching_cycles]
        numerology_mappings = [
            {"mapping": "standard", "offset": 0},
            {"mapping": "isopsephy", "offset": 1},
            {"mapping": "gematria", "offset": 2},
        ]

        space = HypothesisSpace(
            quatrain_id=qid,
            n_interpretations=len(interpretations),
            n_event_candidates=len(event_candidates),
            n_cycle_variants=len(cycle_variants),
            n_numerology_mappings=len(numerology_mappings)
        )

        # Scoring function
        def score_config(interp, event, cycle_idx, numerology):
            interp_score = interp.get("score", 0.0) * 0.2
            cycle_score = 0.3 if cycle_idx < len(cycle_variants) else 0.1
            numerology_score = numerology.get("offset", 0) * 0.05
            # Add some variation based on event
            event_score = 0.3 + (event * 0.01)
            return round(interp_score + event_score + cycle_score + numerology_score, 3)

        # Oracle scores for the space
        oracle_scores = {}
        for idx in range(min(1000, space.total_states)):
            interp, event, cycle, numerology = space.index_to_state(idx)
            oracle_scores[idx] = score_config(
                interpretations[interp] if interp < len(interpretations) else interpretations[0],
                event if event < len(event_candidates) else 0,
                cycle,
                numerology_mappings[numerology] if numerology < len(numerology_mappings) else numerology_mappings[0]
            )

        # Classical sampling
        search_engine = QuantumSearchEngine(entropy)
        classical_results = search_engine.random_sample(space, oracle_scores, n_samples=100)
        classical_best = classical_results[0].composite_score if classical_results else 0

        # Quantum search
        quantum_results = search_engine.grover_search(space, oracle_scores, n_iterations=10)
        quantum_best = quantum_results[0].composite_score if quantum_results else 0

        improvement = ((quantum_best - classical_best) / classical_best * 100) if classical_best > 0 else 0

        print(f"   Event type: {et}, Cycles: {len(cycle_variants)}")
        print(f"   Space: {space.total_states} states")
        print(f"   Classical best: {classical_best:.3f}")
        print(f"   Quantum best: {quantum_best:.3f}")
        print(f"   Improvement: {improvement:.1f}%")

        # Get best cycle and scenario
        best_cycle = matching_cycles[0] if matching_cycles else list(kg.cycles.values())[0]
        best_cycle_name = best_cycle.name if hasattr(best_cycle, 'name') else str(best_cycle)

        # Determine predicted event type from quantum search
        if quantum_results:
            top_config = quantum_results[0]
            # Map cycle_idx to cycle_id
            predicted_cycle = cycle_variants[top_config.cycle_variant] if top_config.cycle_variant < len(cycle_variants) else cycle_variants[0]
            predicted_event = event_candidates[top_config.event_candidate]["name"] if top_config.event_candidate < len(event_candidates) else "unknown"
        else:
            predicted_cycle = cycle_variants[0] if cycle_variants else "unknown"
            predicted_event = "unknown"

        # Determine horizon from cycle
        horizon_map = {
            "political-assassination": "1-10",
            "plague-famine-war": "5-20",
            "religious-conflict-cycle": "10-30",
            "rise-fall-empire": "20-50",
        }
        horizon = horizon_map.get(predicted_cycle, "10-30")

        # Store result
        result = {
            "quatrain_id": qid,
            "french_text": french[:80],
            "status": "hypothesis",
            "event_type_identified": et,
            "cycles_matched": cycle_variants,
            "hypothesis_space_size": space.total_states,
            "classical_best_score": round(classical_best, 3),
            "quantum_best_score": round(quantum_best, 3),
            "improvement_pct": round(improvement, 1),
            "quantum_assisted": True,
            "qrng_entropy_used": entropy is not None,
            "predicted_cycle": predicted_cycle,
            "predicted_event": predicted_event,
            "horizon_years": horizon,
            "confidence": "high" if improvement > 10 else "medium" if improvement > 5 else "low",
            "pattern_strength": round(quantum_best, 3),
            "crypto_anomaly_score": round(crypto_score, 3),
            "past_match_score": round(match_score, 3),
            "top_quantum_configs": [
                {
                    "interp": r.interpretation,
                    "event": r.event_candidate,
                    "cycle": r.cycle_variant,
                    "numerology": r.numerology_mapping,
                    "score": r.composite_score
                }
                for r in quantum_results[:3]
            ]
        }
        experiment_results.append(result)

    # Save results
    output_path = Path("nostradamus/data/processed/quantum_forecast_hypotheses.json")
    with open(output_path, 'w') as f:
        json.dump(experiment_results, f, indent=2)

    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)

    # Aggregate stats
    classical_scores = [r["classical_best_score"] for r in experiment_results]
    quantum_scores = [r["quantum_best_score"] for r in experiment_results]
    improvements = [r["improvement_pct"] for r in experiment_results]

    print(f"\nQuatrains analyzed: {len(experiment_results)}")
    print(f"Classical avg best score: {sum(classical_scores)/len(classical_scores):.3f}")
    print(f"Quantum avg best score: {sum(quantum_scores)/len(quantum_scores):.3f}")
    print(f"Average improvement: {sum(improvements)/len(improvements):.1f}%")

    # High improvement cases
    high_imp = [r for r in experiment_results if r["improvement_pct"] > 10]
    print(f"\nHigh improvement (>10%): {len(high_imp)} cases")

    # Confidence distribution
    confidence_counts = Counter(r["confidence"] for r in experiment_results)
    print(f"\nConfidence distribution:")
    for c, count in confidence_counts.items():
        print(f"  {c}: {count}")

    # Predicted cycles
    cycle_counts = Counter(r["predicted_cycle"] for r in experiment_results)
    print(f"\nPredicted cycles:")
    for c, count in cycle_counts.most_common():
        print(f"  {c}: {count}")

    # Event types predicted
    event_counts = Counter(r["event_type_identified"] for r in experiment_results)
    print(f"\nEvent types:")
    for e, count in event_counts.most_common():
        print(f"  {e}: {count}")

    print(f"\nResults saved to: {output_path}")

    # Qualitative review section
    print("\n" + "=" * 70)
    print("QUALITATIVE REVIEW")
    print("=" * 70)

    print("\nQuatrains where quantum search found notably better fits:")
    for r in sorted(experiment_results, key=lambda x: -x["improvement_pct"])[:5]:
        print(f"\n  {r['quatrain_id']} ({r['improvement_pct']:.1f}% improvement):")
        print(f"    French: {r['french_text'][:50]}...")
        print(f"    Cycle: {r['predicted_cycle']}")
        print(f"    Predicted: {r['predicted_event']}")
        print(f"    Horizon: {r['horizon_years']} years")

    print("\n" + "=" * 70)
    print("NOTE: These are hypotheses, NOT predictions.")
    print("Each represents a plausible scenario based on historical patterns.")
    print("=" * 70)


if __name__ == "__main__":
    main()
