#!/usr/bin/env python3
"""
Per-Issue Breakdown Analysis
For each IssueSignal, compute:
  - Count of supporting quatrains
  - Mean + max cryptographic anomaly
  - Century distribution
  - Top keywords
  - Dominant planetary mix (from keyword symbolism)
Run: python run_issue_breakdown.py
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent / "analysis"))

from nostradamus.analysis.issue_radar import IssueRadar, ISSUE_CATEGORIES
from nostradamus.analysis.tkg_forecaster import load_and_build_kg


# Planetary symbolism for inferring planet dominance from keyword context
PLANET_KEYWORDS = {
    "Mars": ["guerre", "bataille", "combat", "armee", "soldats", "militaire",
             "siege", "invasion", "defait", "sanglant", "mort", "tuer"],
    "Soleil": ["roi", "roy", "regne", "couronne", "soleil", "jour", "lumière",
               "empire", "monarchie", "prince"],
    "Saturn": ["peste", "plague", "famine", "mort", "funeste", "trist", "malheur",
               "chute", "ruine", "sterile"],
    "Lune": ["revolte", "revolution", "emeute", "peuple", "changement", "flot",
             "inondation", "deluge", "eaux"],
    "Venus": ["amour", "alliance", "mariage", "paix", "beaute", "femin", "joie"],
    "Jupiter": ["treaty", "paix", "loi", "religion", "eglise", "expansion", "ordre"],
    "Mercure": ["message", "lettre", "negociation", "commerce", "trafic", "messager"],
}


def infer_planet_from_text(text: str) -> str:
    """Infer dominant planet from text content using keyword matching."""
    text_lower = text.lower()
    scores = {}
    for planet, keywords in PLANET_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[planet] = scores.get(planet, 0) + score

    if not scores:
        return "none"
    return max(scores, key=scores.get)


def main():
    print("=" * 70)
    print("PER-ISSUE BREAKDOWN ANALYSIS")
    print("Anomaly + Planetary + Century distribution per IssueSignal")
    print("=" * 70)

    # Load KG
    kg, kb_events = load_and_build_kg()

    # Load quatrains
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        quatrains_full = json.load(f)

    # Load exhaustive analysis
    with open("nostradamus/data/processed/exhaustive_quatrain_analysis.json", 'r') as f:
        analyses = json.load(f)

    # Build crypto lookup
    crypto_map = {r['quatrain_id']: r['cryptography']['letter_anomaly_score'] for r in quatrains_full}

    # Build quatrain text lookup
    quatrain_text = {r['quatrain_id']: r.get('french', '') for r in quatrains_full}

    print(f"\nQuatrains: {len(analyses)}")
    print(f"Crypto entries: {len(crypto_map)}")

    # ============================================================
    # Group analyses by issue category
    # ============================================================
    issue_data = {issue: [] for issue in ISSUE_CATEGORIES}
    issue_data["none"] = []  # quatrains with no issue match

    for a in analyses:
        qid = a["quatrain_id"]
        issues = a["motifs"]["issue_matches"]
        crypto_score = crypto_map.get(qid, 0.0)
        century = a["century"]
        text = quatrain_text.get(qid, "")

        if not issues:
            issue_data["none"].append({
                "quatrain_id": qid,
                "century": century,
                "crypto_anomaly": crypto_score,
                "keywords": a["motifs"]["keywords"],
                "text": text,
            })
        else:
            for issue in issues:
                if issue in issue_data:
                    issue_data[issue].append({
                        "quatrain_id": qid,
                        "century": century,
                        "crypto_anomaly": crypto_score,
                        "keywords": a["motifs"]["keywords"],
                        "text": text,
                    })

    # ============================================================
    # Compute per-issue statistics
    # ============================================================
    print("\n" + "=" * 70)
    print("PER-ISSUE STATISTICS")
    print("=" * 70)

    results_rows = []

    for issue, label in [(k, v["label"]) for k, v in ISSUE_CATEGORIES.items()]:
        entries = issue_data[issue]
        if not entries:
            continue

        count = len(entries)
        anomalies = [e["crypto_anomaly"] for e in entries]
        mean_anomaly = sum(anomalies) / len(anomalies)
        max_anomaly = max(anomalies)

        # Century distribution
        century_counts = Counter(e["century"] for e in entries)
        century_spread = sorted(century_counts.keys())

        # Top keywords (aggregate across all entries)
        keyword_counter = Counter()
        for e in entries:
            keyword_counter.update(e["keywords"])

        # Infer planet dominance
        planet_counter = Counter()
        for e in entries:
            text = e["text"]
            if text:
                planet = infer_planet_from_text(text)
                if planet != "none":
                    planet_counter[planet] += 1

        # High anomaly rate
        high_anomaly_rate = sum(1 for a in anomalies if a > 0.3) / len(anomalies)

        results_rows.append({
            "issue": issue,
            "label": label,
            "count": count,
            "pct": 100 * count / len(analyses),
            "mean_anomaly": mean_anomaly,
            "max_anomaly": max_anomaly,
            "high_anomaly_rate": high_anomaly_rate,
            "century_spread": century_spread,
            "century_counts": dict(century_counts),
            "top_keywords": keyword_counter.most_common(5),
            "planet_counts": dict(planet_counter.most_common(3)),
        })

    # Sort by count descending
    results_rows.sort(key=lambda x: -x["count"])

    # Print table
    print(f"\n{'Issue':<30} {'Count':>6} {'%':>6} {'MeanAno':>8} {'MaxAno':>8} {'Hi%':>6} {'Planets'}")
    print("-" * 90)

    for r in results_rows:
        planets_str = ", ".join(f"{p}({c})" for p, c in list(r["planet_counts"].items())[:3])
        if not planets_str:
            planets_str = "n/a"
        print(f"{r['label']:<30} {r['count']:>6} {r['pct']:>5.1f}% {r['mean_anomaly']:>8.3f} "
              f"{r['max_anomaly']:>8.3f} {r['high_anomaly_rate']:>5.1%}  {planets_str}")

    # ============================================================
    # Century spread heatmap
    # ============================================================
    print("\n" + "=" * 70)
    print("CENTURY SPREAD PER ISSUE (count per century)")
    print("=" * 70)

    centuries = sorted(set(a["century"] for a in analyses))

    # Header
    header = f"{'Issue':<28}" + "".join(f"C{c:>2}" for c in centuries) + f"{'Total':>6}"
    print(header)
    print("-" * (28 + len(centuries) * 4 + 6))

    for r in results_rows:
        row = f"{r['label'][:28]:<28}"
        for c in centuries:
            count = r["century_counts"].get(c, 0)
            row += f"{count:>3} "
        row += f"{r['count']:>6}"
        print(row)

    # ============================================================
    # Top keywords per issue
    # ============================================================
    print("\n" + "=" * 70)
    print("TOP KEYWORDS PER ISSUE")
    print("=" * 70)

    for r in results_rows:
        kws = ", ".join(f"{k}({c})" for k, c in r["top_keywords"][:8])
        print(f"\n{r['label']} ({r['count']} quatrains):")
        print(f"  {kws}")

    # ============================================================
    # High-anomaly champions per issue
    # ============================================================
    print("\n" + "=" * 70)
    print("HIGHEST ANOMALY QUATRAIN PER ISSUE")
    print("=" * 70)

    for r in results_rows:
        entries_sorted = sorted(issue_data[r["issue"]], key=lambda x: -x["crypto_anomaly"])
        top = entries_sorted[0]
        print(f"\n{r['label']}:")
        print(f"  [{top['quatrain_id']}] anomaly={top['crypto_anomaly']:.3f} century={top['century']}")
        print(f"  Keywords: {dict(top['keywords'])}")
        print(f"  Text: {top['text'][:80]}...")

    # ============================================================
    # None group stats
    # ============================================================
    none_entries = issue_data["none"]
    if none_entries:
        none_anomalies = [e["crypto_anomaly"] for e in none_entries]
        print("\n" + "=" * 70)
        print(f"NO ISSUE MATCH ({len(none_entries)} quatrains)")
        print("=" * 70)
        print(f"  Mean anomaly: {sum(none_anomalies)/len(none_anomalies):.3f}")
        print(f"  Max anomaly:  {max(none_anomalies):.3f}")
        print(f"  High anomaly rate: {sum(1 for a in none_anomalies if a > 0.3)/len(none_anomalies):.1%}")

        # Century distribution of no-match quatrains
        none_centuries = Counter(e["century"] for e in none_entries)
        print(f"  Century spread: {dict(sorted(none_centuries.items()))}")

    # ============================================================
    # Save structured output
    # ============================================================
    output_path = Path("nostradamus/data/processed/issue_breakdown.json")
    output = {
        "total_quatrains": len(analyses),
        "issues": results_rows,
        "none_group": {
            "count": len(none_entries),
            "mean_anomaly": sum(e["crypto_anomaly"] for e in none_entries) / len(none_entries) if none_entries else 0,
            "max_anomaly": max(e["crypto_anomaly"] for e in none_entries) if none_entries else 0,
            "century_distribution": dict(Counter(e["century"] for e in none_entries)),
        }
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {output_path}")


if __name__ == "__main__":
    main()
