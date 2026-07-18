#!/usr/bin/env python3
"""
Nostradamus Issue Radar Runner
Scans all quatrains and almanacs to surface issue signals.
Run: python run_issue_radar.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from nostradamus.analysis.issue_radar import IssueRadar
from nostradamus.analysis.tkg_forecaster import load_and_build_kg


HORIZONS = {
    "short": "0-15 years",
    "medium": "15-30 years",
    "long": "30-65 years",
    "very_long": "65-150 years",
}


def main():
    print("=" * 70)
    print("NOSTRADAMUS ISSUE RADAR")
    print("Text-centered issue detection from quatrains and almanacs")
    print("=" * 70)

    # Load KG
    kg, kb_events = load_and_build_kg()
    print(f"\nKnowledge graph: {len(kg.events)} events, {len(kg.cycles)} cycles")

    # Load quatrains
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        quatrains = json.load(f)
    print(f"Quatrains loaded: {len(quatrains)}")

    # Load almanac corpus
    try:
        from nostradamus.data.almanac_corpus import ALL_ALMANACS
        almanacs = ALL_ALMANACS
        print(f"Almanacs loaded: {len(almanacs)}")
    except Exception as e:
        print(f"Almanac corpus not available: {e}")
        almanacs = None

    # Initialize radar
    radar = IssueRadar(kg=kg, kb_events=kb_events)

    # Scan (minimum 1 quatrain per issue)
    print("\nScanning for issue signals...")
    signals = radar.scan_quatrains(quatrains, almanacs=almanacs, min_quatrain_count=1)
    print(f"Issue signals found: {len(signals)}")

    # Add horizon forecasts
    print("Running horizon forecasts per issue...")
    signals = radar.add_forecasts(signals, quatrains)

    # Sort by pattern strength
    signals.sort(key=lambda s: -s.pattern_strength)

    # Print report
    print("\n" + radar.report(signals))

    # Save results
    output = {
        "total_signals": len(signals),
        "scan_parameters": {
            "quatrain_count": len(quatrains),
            "min_quatrains_per_issue": 1,
        },
        "signals": [s.to_dict() for s in signals],
    }

    out_path = Path("nostradamus/data/processed/issue_radar_results.json")
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    # Show top issue by horizon band
    print("\n" + "=" * 70)
    print("ISSUE SIGNALS BY HORIZON BAND")
    print("=" * 70)

    by_band = {}
    for s in signals:
        band = s.horizon_band
        if band not in by_band:
            by_band[band] = []
        by_band[band].append(s)

    for band in ["short", "medium", "long", "very_long"]:
        if band not in by_band:
            continue
        issues = by_band[band]
        print(f"\n{band.upper()} ({HORIZONS.get(band, '')}):")
        for s in sorted(issues, key=lambda x: -x.pattern_strength)[:5]:
            conf_marker = "*" if s.confidence_band == "high" else ("." if s.confidence_band == "medium" else "")
            print(f"  [{s.quatrain_count:3d}q{conf_marker}] {s.issue_label:<35} strength={s.pattern_strength:.3f} curr={s.current_signal_strength}")

    print("\n" + "=" * 70)
    print("NOTE: These are ISSUE CANDIDATES, not predictions.")
    print("=" * 70)


HORIZONS = {
    "short": "0-15 years",
    "medium": "15-30 years",
    "long": "30-65 years",
    "very_long": "65-150 years",
}


if __name__ == "__main__":
    main()
