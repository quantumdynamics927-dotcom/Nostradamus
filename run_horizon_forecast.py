#!/usr/bin/env python3
"""
Run TKG Forecast Analysis with Horizon Bands
Search across multiple time horizons: short (0-15), medium (15-30), long (30-65), very_long (65+)
"""

import sys
import json
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent / "analysis"))


def main():
    print("=" * 70)
    print("TKG FORECAST ANALYSIS WITH HORIZON BANDS")
    print("Searching across multiple time horizons")
    print("=" * 70)

    # Import forecaster
    from nostradamus.analysis.tkg_forecaster import (
        TKGForecaster, load_and_build_kg, HORIZON_BANDS, CYCLE_HORIZON_MAP
    )

    # Build KG
    kg, kb_events = load_and_build_kg()
    print(f"\nKnowledge graph: {len(kg.events)} events, {len(kg.cycles)} cycles")

    # Show horizon definitions
    print("\n" + "-" * 50)
    print("HORIZON BANDS:")
    for band, info in HORIZON_BANDS.items():
        years = info["years"]
        print(f"  {band}: {years[0]}-{years[1]} years - {info['description']}")

    print("\n" + "-" * 50)
    print("CYCLE TO HORIZON MAPPING:")
    for cycle, (min_y, max_y) in CYCLE_HORIZON_MAP.items():
        print(f"  {cycle}: {min_y}-{max_y} years")

    # Load analysis results
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        results = json.load(f)

    # Get high-crypto unmatched quatrains
    candidates = [
        r for r in results
        if r.get("cryptography", {}).get("letter_anomaly_score", 0) > 0.5
        and r.get("history", {}).get("match_score", 0) < 0.5
    ]

    print(f"\nAnalyzing {len(candidates)} high-crypto unmatched quatrains...")

    # Initialize forecaster
    forecaster = TKGForecaster(kg, None)

    # Run analysis
    horizon_results = {band: [] for band in HORIZON_BANDS.keys()}
    all_hypotheses = []

    for i, r in enumerate(candidates[:20]):  # Top 20
        q = {
            "century": int(r["quatrain_id"].split("-Q")[0].replace("C", "")),
            "quatrain": int(r["quatrain_id"].split("-Q")[1]),
            "french": r["french"]
        }
        astro = r.get("astrology", {})

        hypothesis = forecaster.analyze_quatrain(q, astro, kb_events)
        all_hypotheses.append(hypothesis)

        # Categorize by horizon band
        band = hypothesis.horizon_band if hasattr(hypothesis, 'horizon_band') else "short"
        if band in horizon_results:
            horizon_results[band].append(hypothesis)

        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1}/{min(20, len(candidates))}")

    # Print results by horizon band
    print("\n" + "=" * 70)
    print("RESULTS BY HORIZON BAND")
    print("=" * 70)

    for band in ["short", "medium", "long", "very_long"]:
        hypotheses = horizon_results[band]
        if not hypotheses:
            continue

        info = HORIZON_BANDS[band]
        print(f"\n{'='*60}")
        print(f"{band.upper()} ({info['years'][0]}-{info['years'][1]} years)")
        print(f"{info['description']}")
        print(f"{'='*60}")
        print(f"Count: {len(hypotheses)}")

        # Group by cycle
        by_cycle = Counter(h.cycle_match for h in hypotheses)
        print(f"\nBy cycle:")
        for cycle, count in by_cycle.most_common():
            print(f"  {cycle}: {count}")

        # Group by event type
        by_event = Counter(h.event_type_predicted for h in hypotheses)
        print(f"\nBy predicted event type:")
        for et, count in by_event.most_common():
            print(f"  {et}: {count}")

        # Show top hypotheses
        print(f"\nTop hypotheses:")
        for h in sorted(hypotheses, key=lambda x: -x.pattern_strength)[:3]:
            print(f"\n  {h.quatrain_id} (strength={h.pattern_strength:.3f})")
            print(f"    French: {h.french_text[:50]}...")
            print(f"    Cycle: {h.cycle_name}")
            print(f"    Predicted: {h.event_type_predicted}")
            print(f"    Horizon: {h.horizon_years} ({h.confidence})")

    # Summary statistics
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total = len(all_hypotheses)
    print(f"\nTotal hypotheses: {total}")

    band_counts = {band: len(hs) for band, hs in horizon_results.items()}
    print(f"\nHorizon distribution:")
    for band, count in band_counts.items():
        pct = 100 * count / total if total > 0 else 0
        print(f"  {band}: {count} ({pct:.1f}%)")

    # Confidence distribution
    confidence_counts = Counter(h.confidence for h in all_hypotheses)
    print(f"\nConfidence distribution:")
    for conf, count in confidence_counts.most_common():
        print(f"  {conf}: {count}")

    # Pattern strength by horizon
    print(f"\nAverage pattern strength by horizon:")
    for band in ["short", "medium", "long", "very_long"]:
        hs = horizon_results[band]
        if hs:
            avg = sum(h.pattern_strength for h in hs) / len(hs)
            print(f"  {band}: {avg:.3f}")

    # Save results
    output = {
        "all_hypotheses": [h.to_dict() for h in all_hypotheses],
        "by_horizon_band": {
            band: [h.to_dict() for h in hs]
            for band, hs in horizon_results.items()
        },
        "horizon_definitions": HORIZON_BANDS,
        "cycle_horizon_map": CYCLE_HORIZON_MAP
    }

    out_path = Path("nostradamus/data/processed/horizon_forecast_results.json")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {out_path}")

    print("\n" + "=" * 70)
    print("NOTE: These are HYPOTHESES, not predictions.")
    print("Every scenario is anchored in Nostradamus's quatrains and historical cycles.")
    print("=" * 70)


if __name__ == "__main__":
    main()
