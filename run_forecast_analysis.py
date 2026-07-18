#!/usr/bin/env python3
"""
TKG Forecast Analysis CLI
Run temporal knowledge graph forecasting on candidate quatrains.
"""

import sys
import json
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
    print("TKG FORECAST ANALYSIS")
    print("Chain-of-History Reasoning for Future Event Hypotheses")
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
            else:
                print("\nQRNG pool not found - using PRNG fallback")
        except Exception as e:
            print(f"\nQRNG load failed: {e} - using PRNG fallback")
    else:
        print("\nQRNG not available - using PRNG fallback")

    # Import after path setup
    from nostradamus.analysis.tkg_forecaster import generate_forecast, load_and_build_kg

    # Build knowledge graph
    print("\nBuilding knowledge graph...")
    kg, kb_events = load_and_build_kg()
    print(f"  {len(kg.events)} events, {len(kg.cycles)} cycles")

    # Run forecast analysis
    print("\n" + "=" * 70)
    print("RUNNING FORECAST ANALYSIS")
    print("=" * 70)

    hypotheses = generate_forecast(
        candidate_filter="high_crypto",
        max_quatrains=20,
        entropy_service=entropy
    )

    print(f"\nGenerated {len(hypotheses)} hypotheses")

    # Sort by pattern strength
    hypotheses.sort(key=lambda h: -h["pattern_strength"])

    print("\n" + "=" * 70)
    print("TOP 10 HYPOTHESES BY PATTERN STRENGTH")
    print("=" * 70)

    for i, h in enumerate(hypotheses[:10]):
        print(f"\n{i+1}. {h['quatrain_id']}")
        print(f"   French: {h['french_text'][:60]}...")
        print(f"   Status: {h['status']}")
        print(f"   Cycle: {h['cycle_name']} ({h['cycle_match']})")
        print(f"   Pattern strength: {h['pattern_strength']:.3f}")
        print(f"   P-value approx: {h['p_value_approximate']:.4f}")
        print(f"   Predicted event: {h['event_type_predicted']}")
        print(f"   Region cluster: {h['region_cluster']}")
        print(f"   Horizon: {h['horizon_years']} ({h['confidence']} confidence)")
        print(f"   Supporting instances: {h['supporting_cycle_instances']}")
        print(f"   QRNG entropy used: {h['qrng_entropy_used']}")

        if h['scenarios']:
            print(f"   Alternative scenarios:")
            for j, s in enumerate(h['scenarios'][1:4], 1):
                print(f"     {j}. {s['event_type']} in {s['region_cluster']} ({s['horizon_years']})")

    # Save results
    output_path = Path("nostradamus/data/processed/forecast_hypotheses.json")
    with open(output_path, 'w') as f:
        json.dump(hypotheses, f, indent=2)

    print("\n" + "=" * 70)
    print("OUTPUT")
    print("=" * 70)
    print(f"Saved {len(hypotheses)} hypotheses to: {output_path}")

    # Summary stats
    confidence_counts = {"high": 0, "medium": 0, "low": 0}
    for h in hypotheses:
        confidence_counts[h['confidence']] += 1

    print(f"\nConfidence distribution:")
    print(f"  High: {confidence_counts['high']}")
    print(f"  Medium: {confidence_counts['medium']}")
    print(f"  Low: {confidence_counts['low']}")

    # Event type predictions
    event_types = {}
    for h in hypotheses:
        et = h['event_type_predicted']
        event_types[et] = event_types.get(et, 0) + 1

    print(f"\nPredicted event types:")
    for et, count in sorted(event_types.items(), key=lambda x: -x[1]):
        print(f"  {et}: {count}")

    print("\n" + "=" * 70)
    print("NOTE: These are HYPOTHESES, not predictions.")
    print("Each represents a plausible future scenario based on historical patterns.")
    print("=" * 70)


if __name__ == "__main__":
    main()
