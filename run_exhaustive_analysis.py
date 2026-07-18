#!/usr/bin/env python3
"""
Exhaustive Quatrain Analysis with Issue Radar
Analyzes every quatrain individually and produces:
  1. Per-quatrain motif/issue report (JSON)
  2. Issue-radar aggregated report (JSON)
  3. Human-readable summary (TXT)

Run: python run_exhaustive_analysis.py
"""

import json
import sys
from pathlib import Path
from collections import Counter
import html

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from nostradamus.analysis.issue_radar import IssueRadar, ISSUE_CATEGORIES
from nostradamus.analysis.tkg_forecaster import load_and_build_kg


def main():
    print("=" * 70)
    print("EXHAUSTIVE QUATRAIN ANALYSIS WITH ISSUE RADAR")
    print("=" * 70)

    # Load KG
    kg, kb_events = load_and_build_kg()
    print(f"\nKG: {len(kg.events)} events, {len(kg.cycles)} cycles")

    # Load quatrains
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        quatrains = json.load(f)
    print(f"Quatrains: {len(quatrains)}")

    # Initialize radar
    radar = IssueRadar(kg=kg, kb_events=kb_events)

    # ============================================================
    # STEP 1: Per-quatrain motif extraction
    # ============================================================
    print("\n[1/3] Extracting motifs from all quatrains...")

    quatrain_analyses = []
    motif_counter = Counter()
    issue_quatrain_map = {issue: [] for issue in ISSUE_CATEGORIES}

    for q in quatrains:
        qid = q.get("quatrain_id", "")
        french_raw = q.get("french", "")
        french = html.unescape(french_raw)
        motifs = radar._extract_motifs(french, qid)

        # Track motifs
        motif_counter.update(motifs.get("keywords_matched", Counter()))
        for issue in motifs.get("issue_matches", []):
            if issue in issue_quatrain_map:
                issue_quatrain_map[issue].append(qid)

        quatrain_analyses.append({
            "quatrain_id": qid,
            "century": int(qid.split("-Q")[0].replace("C", "")),
            "quatrain_num": int(qid.split("-Q")[1]),
            "french": french[:200],
            "english": q.get("english", "")[:200],
            "motifs": {
                "disaster_types": motifs.get("disaster_types", []),
                "space_types": motifs.get("space_types", []),
                "issue_matches": motifs.get("issue_matches", []),
                "keywords": dict(motifs.get("keywords_matched", {})),
                "symbols": motifs.get("symbols", [])[:10],
                "locations": motifs.get("locations", []),
                "astro_refs": motifs.get("astro_refs", []),
            },
            "signal_count": len(motifs.get("issue_matches", [])),
            "top_issue": motifs.get("issue_matches", ["none"])[0] if motifs.get("issue_matches") else "none",
        })

    print(f"  Motif extraction complete: {len(quatrain_analyses)} quatrains")

    # ============================================================
    # STEP 2: Issue radar aggregation
    # ============================================================
    print("\n[2/3] Building issue signals...")

    signals = radar.scan_quatrains(quatrains, min_quatrain_count=1)
    signals = radar.add_forecasts(signals, quatrains)
    signals.sort(key=lambda s: -s.pattern_strength)

    print(f"  Issue signals: {len(signals)}")

    # ============================================================
    # STEP 3: Build summary statistics
    # ============================================================
    print("\n[3/3] Generating summary statistics...")

    # Per-quatrain stats
    with_signals = sum(1 for a in quatrain_analyses if a["signal_count"] > 0)
    no_signals = len(quatrain_analyses) - with_signals

    # Issue distribution
    issue_distribution = {}
    for issue, qids in issue_quatrain_map.items():
        issue_distribution[issue] = {
            "count": len(qids),
            "quatrain_ids": qids,
            "label": ISSUE_CATEGORIES.get(issue, {}).get("label", issue),
        }

    # Top motifs
    top_motifs = dict(motif_counter.most_common(30))

    # Centuries breakdown
    century_stats = {}
    for a in quatrain_analyses:
        c = a["century"]
        if c not in century_stats:
            century_stats[c] = {"total": 0, "with_signals": 0, "issues": Counter()}
        century_stats[c]["total"] += 1
        century_stats[c]["with_signals"] += 1 if a["signal_count"] > 0 else 0
        century_stats[c]["issues"].update(a["motifs"]["issue_matches"])

    # ============================================================
    # SAVE OUTPUTS
    # ============================================================
    out_dir = Path("nostradamus/data/processed")
    out_dir.mkdir(exist_ok=True)

    # 1. Per-quatrain analysis JSON
    qa_path = out_dir / "exhaustive_quatrain_analysis.json"
    with open(qa_path, 'w') as f:
        json.dump(quatrain_analyses, f, indent=2)
    print(f"\nSaved: {qa_path}")

    # 2. Issue radar results JSON (already has signals)
    ir_path = out_dir / "issue_radar_results.json"
    with open(ir_path, 'w') as f:
        json.dump({
            "total_signals": len(signals),
            "scan_parameters": {
                "quatrain_count": len(quatrains),
                "min_quatrains_per_issue": 1,
            },
            "issue_distribution": {k: {"count": v["count"], "label": v["label"]} for k, v in issue_distribution.items()},
            "signals": [s.to_dict() for s in signals],
        }, f, indent=2)
    print(f"Saved: {ir_path}")

    # 3. Human-readable TXT report
    txt_path = out_dir / "exhaustive_analysis_report.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        _write_txt_report(f, quatrains, quatrain_analyses, signals,
                          issue_distribution, top_motifs, century_stats)
    print(f"Saved: {txt_path}")

    # ============================================================
    # PRINT SUMMARY
    # ============================================================
    print("\n" + "=" * 70)
    print("EXHAUSTIVE ANALYSIS SUMMARY")
    print("=" * 70)

    print(f"\nQuatrains analyzed: {len(quatrain_analyses)}")
    print(f"With motif signals: {with_signals} ({100*with_signals/len(quatrain_analyses):.1f}%)")
    print(f"No signals detected: {no_signals} ({100*no_signals/len(quatrain_analyses):.1f}%)")

    print(f"\nIssue signals detected: {len(signals)}")
    print(f"Top motifs: {list(top_motifs.keys())[:10]}")

    print("\n--- ISSUE SIGNALS BY CONFIDENCE ---")
    for sig in sorted(signals, key=lambda s: -s.pattern_strength):
        pct = 100 * sig.quatrain_count / len(quatrains)
        print(f"  [{sig.confidence_band.upper():6s}] {sig.quatrain_count:3d}q ({pct:5.1f}%) {sig.issue_label:<40} horizon={sig.horizon_band}")

    print("\n--- PER-CENTURY BREAKDOWN ---")
    for c in sorted(century_stats.keys()):
        cs = century_stats[c]
        pct = 100 * cs["with_signals"] / cs["total"] if cs["total"] > 0 else 0
        top_issues = [k for k, _ in cs["issues"].most_common(3)]
        print(f"  Century {c}: {cs['total']:3d}q | {cs['with_signals']:3d} with signals ({pct:.0f}%) | top issues: {top_issues}")

    print("\n--- TOP 20 MOTIFS ---")
    for motif, count in motif_counter.most_common(20):
        pct = 100 * count / len(quatrains)
        print(f"  {motif:<30s} {count:4d} ({pct:5.1f}%)")

    print("\n" + "=" * 70)
    print("NOTE: These are ISSUE CANDIDATES, not predictions.")
    print("=" * 70)
    print(f"\nFull reports saved to:")
    print(f"  {qa_path}")
    print(f"  {ir_path}")
    print(f"  {txt_path}")


def _write_txt_report(f, quatrains, analyses, signals,
                      issue_dist, top_motifs, century_stats):
    """Write human-readable TXT report."""
    f.write("=" * 70 + "\n")
    f.write("NOSTRADAMUS EXHAUSTIVE QUATRAIN ANALYSIS REPORT\n")
    f.write("=" * 70 + "\n\n")

    # Header stats
    total = len(analyses)
    with_sigs = sum(1 for a in analyses if a["signal_count"] > 0)
    f.write(f"Total quatrains analyzed : {total}\n")
    f.write(f"With motif signals       : {with_sigs} ({100*with_sigs/total:.1f}%)\n")
    f.write(f"No signals              : {total - with_sigs} ({100*(total-with_sigs)/total:.1f}%)\n")
    f.write(f"Issue categories        : {len(signals)}\n\n")

    # Issue signals
    f.write("=" * 70 + "\n")
    f.write("ISSUE SIGNALS (sorted by pattern strength)\n")
    f.write("=" * 70 + "\n\n")

    for sig in signals:
        pct = 100 * sig.quatrain_count / total
        f.write(f"[{sig.confidence_band.upper():6s}] {sig.quatrain_count:3d}q ({pct:5.1f}%) | {sig.issue_label}\n")
        f.write(f"           Horizon: {sig.horizon_years} ({sig.horizon_band}) | Current: {sig.current_signal_strength}\n")
        f.write(f"           Cycles: {sig.cycle_matches or 'none'}\n")
        f.write(f"           Top symbols: {', '.join(sig.dominant_symbols[:6])}\n")
        f.write(f"           Top quatrain: {sig.source_quatrain_ids[0] if sig.source_quatrain_ids else 'n/a'}\n")
        f.write("\n")

    # Century breakdown
    f.write("=" * 70 + "\n")
    f.write("PER-CENTURY BREAKDOWN\n")
    f.write("=" * 70 + "\n\n")

    for c in sorted(century_stats.keys()):
        cs = century_stats[c]
        pct = 100 * cs["with_signals"] / cs["total"] if cs["total"] > 0 else 0
        top = [f"{k}({v})" for k, v in cs["issues"].most_common(5)]
        f.write(f"C{c}: {cs['total']:3d}q | {cs['with_signals']:3d} signals ({pct:.0f}%) | {', '.join(top)}\n")

    # Top motifs
    f.write("\n" + "=" * 70 + "\n")
    f.write("TOP 50 MOTIFS ACROSS ALL QUATRAINS\n")
    f.write("=" * 70 + "\n\n")

    for motif, count in top_motifs.items():
        pct = 100 * count / total
        bar = "#" * int(pct / 2)
        f.write(f"  {motif:<30s} {count:4d} ({pct:5.1f}%) {bar}\n")

    # Sample quatrains per issue
    f.write("\n" + "=" * 70 + "\n")
    f.write("SAMPLE QUATRAINS PER ISSUE (top 3 by century diversity)\n")
    f.write("=" * 70 + "\n\n")

    for sig in signals[:8]:
        f.write(f"\n--- {sig.issue_label} ({sig.quatrain_count} quatrains) ---\n")
        for qid in sig.source_quatrain_ids[:3]:
            a = next((x for x in analyses if x["quatrain_id"] == qid), None)
            if a:
                f.write(f"  [{qid}] {a['french'][:70]}...\n")
                f.write(f"           issues: {a['motifs']['issue_matches']} | symbols: {a['motifs']['symbols'][:4]}\n")

    f.write("\n" + "=" * 70 + "\n")
    f.write("NOTE: These are ISSUE CANDIDATES, not predictions.\n")
    f.write("Every signal is a hypothesis rooted in Nostradamus's writings + cycle models.\n")
    f.write("=" * 70 + "\n")


if __name__ == "__main__":
    main()
