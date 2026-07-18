#!/usr/bin/env python3
"""
Quantum Hypothesis Search CLI
Run quantum-assisted search over the combinatorial hypothesis space.
"""

import sys
import json
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

try:
    import pickle
    from entropy.qrng_service import EntropyService
    QRNG_AVAILABLE = True
except:
    QRNG_AVAILABLE = False


def main():
    print("=" * 70)
    print("QUANTUM HYPOTHESIS SEARCH")
    print("Searching the combinatorial space of quatrain interpretations")
    print("=" * 70)

    # Load QRNG
    entropy = None
    if QRNG_AVAILABLE:
        try:
            qrng_path = Path("nostradamus/data/entropy_sources/qrng/entropy_service.pkl")
            if qrng_path.exists():
                with open(qrng_path, 'rb') as f:
                    entropy = pickle.load(f)
                print(f"\nQRNG loaded: {entropy._pool.remaining:,} bits available")
            else:
                print("\nQRNG pool not found - using PRNG fallback")
        except Exception as e:
            print(f"\nQRNG load failed: {e} - using PRNG fallback")
    else:
        print("\nQRNG not available - using PRNG fallback")

    # Import quantum search
    from nostradamus.analysis.quantum_hypothesis_search import (
        QuantumHypothesisRanker,
        QuantumMonteCarloValidator,
        QuantumSearchEngine,
        HypothesisSpace,
        quantum_enhanced_forecast
    )

    # Demo: Show hypothesis space sizes
    print("\n" + "=" * 70)
    print("HYPOTHESIS SPACE SIZES")
    print("=" * 70)

    # Example: C10-Q99 (strongest pattern match)
    example_space = HypothesisSpace(
        quatrain_id="C10-Q99",
        n_interpretations=3,  # literal, symbolic, numerological
        n_event_candidates=20,  # top 20 candidate events
        n_cycle_variants=4,  # 4 standard cycles
        n_numerology_mappings=5  # different gematria approaches
    )

    print(f"\nC10-Q99 hypothesis space:")
    print(f"  Interpretations: {example_space.n_interpretations}")
    print(f"  Event candidates: {example_space.n_event_candidates}")
    print(f"  Cycle variants: {example_space.n_cycle_variants}")
    print(f"  Numerology mappings: {example_space.n_numerology_mappings}")
    print(f"  Total states: {example_space.total_states:,}")

    # Show state encoding
    print(f"\nState encoding example:")
    idx = 0
    interp, event, cycle, numerology = example_space.index_to_state(idx)
    print(f"  Index {idx} -> interp={interp}, event={event}, cycle={cycle}, numerology={numerology}")

    idx = example_space.total_states - 1
    interp, event, cycle, numerology = example_space.index_to_state(idx)
    print(f"  Index {idx} -> interp={interp}, event={event}, cycle={cycle}, numerology={numerology}")

    # Run demo search
    print("\n" + "=" * 70)
    print("DEMO: QUANTUM SEARCH")
    print("=" * 70)

    # Simulated oracle scores
    oracle_scores = {}
    for idx in range(min(1000, example_space.total_states)):
        # Simulate scoring: some configurations score higher
        interp, event, cycle, numerology = example_space.index_to_state(idx)
        score = (interp * 0.2 + event * 0.01 + cycle * 0.1 + numerology * 0.05)
        score += random.random() * 0.3  # Add noise
        oracle_scores[idx] = score

    search_engine = QuantumSearchEngine(entropy)

    print(f"\nRunning Grover search on {len(oracle_scores)} states...")
    results = search_engine.grover_search(example_space, oracle_scores, n_iterations=10)

    print(f"\nTop 5 configurations found:")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. Score={r.composite_score:.3f} (quantum_suggested={r.is_quantum_suggested})")
        print(f"     interp={r.interpretation}, event={r.event_candidate}, cycle={r.cycle_variant}, numerology={r.numerology_mapping}")

    # Compare with random sampling
    print("\n" + "-" * 50)
    print("Comparing with classical random sampling...")

    classical_results = search_engine.random_sample(example_space, oracle_scores, n_samples=100)

    print(f"\nClassical random sampling top 5:")
    for i, r in enumerate(classical_results[:5], 1):
        print(f"  {i}. Score={r.composite_score:.3f}")

    quantum_max = max(r.composite_score for r in results)
    classical_max = max(r.composite_score for r in classical_results)

    print(f"\nBest quantum score: {quantum_max:.3f}")
    print(f"Best classical score: {classical_max:.3f}")

    # Run on real data
    print("\n" + "=" * 70)
    print("REAL DATA: QUANTUM-ASSISTED FORECAST")
    print("=" * 70)

    from nostradamus.analysis.tkg_forecaster import load_and_build_kg
    kg, kb_events = load_and_build_kg()

    # Load a sample quatrain
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        results = json.load(f)

    # Find C10-Q99
    target = None
    for r in results:
        if r["quatrain_id"] == "C10-Q99":
            target = r
            break

    if target:
        q = {
            "century": 10,
            "quatrain": 99,
            "french": target["french"]
        }
        astro = target.get("astrology", {})

        print(f"\nAnalyzing {target['quatrain_id']}:")
        print(f"  French: {target['french'][:60]}...")

        result = quantum_enhanced_forecast(q, astro, kb_events, entropy)

        print(f"\nQuantum-assisted hypothesis:")
        print(f"  Status: {result['status']}")
        print(f"  Cycle: {result.get('cycle_name', 'N/A')}")
        print(f"  Predicted event: {result['event_type_predicted']}")
        print(f"  Horizon: {result.get('horizon_years', 'N/A')}")
        print(f"  Pattern strength: {result.get('pattern_strength', 0):.3f}")
        print(f"  Quantum assisted: {result.get('quantum_assisted', False)}")

    print("\n" + "=" * 70)
    print("NOTE: This is classical simulation of quantum search.")
    print("For real quantum advantage, connect to IBM Q or D-Wave.")
    print("=" * 70)


if __name__ == "__main__":
    main()
