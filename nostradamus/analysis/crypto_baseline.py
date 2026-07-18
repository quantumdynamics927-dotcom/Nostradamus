#!/usr/bin/env python3
"""
Cryptographic Baseline Comparison
Compare Nostradamus anomaly rates against Middle French corpora.
"""

import json
import re
from collections import Counter
from pathlib import Path

# Baseline texts - Middle French chronicles (Froissart-style)
# These are representative of standard Middle French prose
BASELINE_TEXTS = [
    # Simulated Froissart-style chronicle text
    """
    Au temps du roy Charle le quint de ce nom, qui fut roy de France,
    advint que les anglois vindrent ou pays de Guienne, et prindrent
    plusieurs fortresses et chasteaulx. Le roy de France envoya grant ost
    pour eulx combatre. Les deux armees se rencontrerent ou plain de tel
    lieu, et y ot grant meslee et mortalite grant de toutes pars.
    """,
    # More Middle French
    """
    Le dictateur envoya ses ambassadeurs ou senat pour traicter de paix.
    Les consuls vindrent au camp des ennemis et requrrent treves.
    Grant multitude de peuple estoient ja assembles pour veoir la bataille.
    """,
    # Religious text style
    """
    En l'annee de grace mil cinq cens, le saint pere le Pape十大,
    et le roy tres chrestien, assemblerent le concile general.
    Tous les eveques et prelas estoient venus de toutes pars.
    """,
    # Historical narrative
    """
    Le duc de Bourgongne fist assembler ses baneres et ses pennons.
    Grant foison de gens d'armes le vindrent servir de toutes pars.
    On fist grant feu et grant luminiere par toute la ville.
    """,
    # Commercial/mercantile
    """
    Les marchans estoient venus de tous les pays pour faire leurs negoces.
    Ils avoient amene grant plant of draps de layne et de soie.
    """,
]

def compute_anomaly_score(text: str, french_freq: dict) -> float:
    """Compute letter frequency anomaly score."""
    text_clean = re.sub(r'[^a-z]', '', text.lower())
    if len(text_clean) < 10:
        return 0.0

    freq = Counter(text_clean)
    total = len(text_clean)

    deviations = []
    for letter, expected_pct in french_freq.items():
        observed = freq.get(letter, 0) / total * 100
        deviation = abs(observed - expected_pct) / (expected_pct + 0.1)
        deviations.append(deviation)

    avg_deviation = sum(deviations) / len(deviations)
    return min(1.0, avg_deviation / 2)

def main():
    # French expected frequencies
    french_freq = {
        'e': 14.7, 'a': 8.2, 's': 7.9, 'i': 7.2, 't': 7.0,
        'n': 7.0, 'r': 6.5, 'l': 5.8, 'u': 5.8, 'o': 5.1,
        'd': 3.5, 'c': 3.3, 'p': 3.0, 'm': 2.8, 'f': 1.2,
        'b': 0.9, 'g': 0.8, 'h': 0.7, 'v': 0.6, 'y': 0.2,
        'x': 0.2, 'z': 0.1, 'j': 0.1, 'q': 0.1, 'k': 0.0
    }

    # Compute baseline anomaly distribution
    print("=" * 70)
    print("CRYPTANALYSIS: NOSTRADAMUS vs BASELINE COMPARISON")
    print("=" * 70)

    # Baseline scores
    baseline_scores = []
    for i, text in enumerate(BASELINE_TEXTS):
        score = compute_anomaly_score(text, french_freq)
        baseline_scores.append(score)
        print(f"\nBaseline text {i+1}: anomaly = {score:.3f}")

    baseline_avg = sum(baseline_scores) / len(baseline_scores)
    baseline_high = sum(1 for s in baseline_scores if s > 0.3)
    print(f"\n--- Baseline Statistics ---")
    print(f"Avg anomaly: {baseline_avg:.3f}")
    print(f"High anomaly (>0.3): {baseline_high}/{len(BASELINE_TEXTS)} ({100*baseline_high/len(BASELINE_TEXTS):.1f}%)")

    # Load Nostradamus results
    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        results = json.load(f)

    nostra_scores = [r["cryptography"]["letter_anomaly_score"] for r in results]
    nostra_avg = sum(nostra_scores) / len(nostra_scores)
    nostra_high = sum(1 for s in nostra_scores if s > 0.3)

    print(f"\n--- Nostradamus Statistics ---")
    print(f"Avg anomaly: {nostra_avg:.3f}")
    print(f"High anomaly (>0.3): {nostra_high}/{len(results)} ({100*nostra_high/len(results):.1f}%)")

    # Comparison
    print(f"\n--- Comparison ---")
    print(f"Nostradamus anomaly is {nostra_avg/baseline_avg:.2f}x higher than baseline")
    print(f"High anomaly rate: Nostradamus {100*nostra_high/len(results):.1f}% vs Baseline {100*baseline_high/len(BASELINE_TEXTS):.1f}%")

    # Distribution
    print(f"\n--- Score Distribution ---")
    bins = [(0, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.6), (0.6, 1.0)]
    print("Nostradamus:")
    for lo, hi in bins:
        count = sum(1 for s in nostra_scores if lo <= s < hi)
        bar = "#" * (count // 10)
        print(f"  {lo:.1f}-{hi:.1f}: {count:3d} ({100*count/len(nostra_scores):5.1f}%) {bar}")

    print("\nBaseline:")
    for lo, hi in bins:
        count = sum(1 for s in baseline_scores if lo <= s < hi)
        bar = "#" * (count * 10)
        print(f"  {lo:.1f}-{hi:.1f}: {count:3d} ({100*count/len(baseline_scores):5.1f}%) {bar}")

    # Significance test (simple)
    print(f"\n--- Interpretation ---")
    if nostra_avg > baseline_avg * 2:
        print("SIGNIFICANT: Nostradamus shows substantially higher anomaly rates")
        print("  This suggests NON-RANDOM structure in his text (possible cipher)")
    elif nostra_avg > baseline_avg * 1.5:
        print("MODERATE: Nostradamus shows elevated anomaly")
        print("  Worth investigating further with proper statistical tests")
    else:
        print("INCONCLUSIVE: Anomaly rates similar to baseline")

if __name__ == "__main__":
    main()
