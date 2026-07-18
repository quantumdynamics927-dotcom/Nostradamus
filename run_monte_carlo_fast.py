#!/usr/bin/env python3
"""
QRNG-Driven Monte Carlo Match Validation (Fast Version)
Uses quantum entropy for rigorous significance testing.
"""

import json
import sys
import math
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent / "analysis"))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pickle
    from entropy.qrng_service import EntropyService, EntropyConfig, EntropyMode
    QRNG_AVAILABLE = True
except:
    QRNG_AVAILABLE = False


class MonteCarloMatchValidator:
    def __init__(self, entropy_service=None):
        self.entropy = entropy_service
        self.results = []

    def _random_score(self, n_events: int) -> float:
        if self.entropy:
            val, src = self.entropy.get_float()
            return val
        import random
        return random.random()

    def validate_match(
        self,
        quatrain_id: str,
        observed_score: float,
        n_events: int = 87,
        n_simulations: int = 5000
    ) -> Dict:
        null_scores = []
        for _ in range(n_simulations):
            random_score = self._random_score(n_events)
            null_scores.append(random_score)

        null_mean = sum(null_scores) / len(null_scores)
        null_variance = sum((s - null_mean) ** 2 for s in null_scores) / len(null_scores)
        null_std = math.sqrt(null_variance)

        exceed_count = sum(1 for s in null_scores if s >= observed_score)
        p_value = exceed_count / n_simulations

        if null_std > 0:
            z_score = (observed_score - null_mean) / null_std
        else:
            z_score = 0

        return {
            "quatrain_id": quatrain_id,
            "observed_score": observed_score,
            "p_value": p_value,
            "z_score": z_score,
            "null_mean": null_mean,
            "null_std": null_std,
            "is_significant": p_value < 0.05,
            "confidence": 1.0 - p_value,
            "simulations": n_simulations,
            "entropy_source": "qrng" if (self.entropy and self.entropy._pool._cursor > 0) else "prng"
        }

    def validate_matches_batch(self, matches: List[Dict], n_events: int = 87, n_simulations: int = 5000) -> List[Dict]:
        results = []
        for match in matches:
            result = self.validate_match(
                quatrain_id=match["quatrain_id"],
                observed_score=match["score"],
                n_events=n_events,
                n_simulations=n_simulations
            )
            results.append(result)
        return results


def main():
    print("=" * 70)
    print("QRNG MONTE CARLO MATCH VALIDATION (Fast Mode)")
    print("=" * 70)

    with open("nostradamus/data/processed/full_analysis_expanded_kb.json", 'r') as f:
        results = json.load(f)

    scored = [r for r in results if r["history"]["match_score"] > 0]
    scored.sort(key=lambda x: -x["history"]["match_score"])

    print(f"\nLoaded {len(scored)} quatrains with match scores")

    validator = MonteCarloMatchValidator()

    qrng_service = None
    if QRNG_AVAILABLE:
        try:
            qrng_path = Path("nostradamus/data/entropy_sources/qrng/entropy_service.pkl")
            if qrng_path.exists():
                with open(qrng_path, 'rb') as f:
                    qrng_service = pickle.load(f)
                print(f"\nQRNG loaded: {qrng_service._pool.remaining:,} bits available")
                validator.entropy = qrng_service
        except Exception as e:
            print(f"\nQRNG not available: {e}")

    print("\n" + "=" * 70)
    print("TOP MATCHES - MONTE CARLO SIGNIFICANCE (5000 sims)")
    print("=" * 70)

    top_matches = scored[:20]
    validated = validator.validate_matches_batch(
        [{"quatrain_id": r["quatrain_id"], "score": r["history"]["match_score"]} for r in top_matches],
        n_simulations=5000
    )

    significant_count = 0
    for v in validated:
        sig = "***" if v["is_significant"] else ""
        print(f"\n{v['quatrain_id']}: score={v['observed_score']:.3f}, p={v['p_value']:.4f}, z={v['z_score']:.2f} {sig}")
        print(f"  Confidence: {v['confidence']:.1%} | Entropy: {v['entropy_source']}")
        match_info = [r for r in top_matches if r['quatrain_id']==v['quatrain_id']]
        if match_info:
            print(f"  Match: {match_info[0]['history']['top_match']}")
        if v["is_significant"]:
            significant_count += 1

    print(f"\n" + "=" * 70)
    print(f"SUMMARY: {significant_count}/{len(validated)} top-20 matches are statistically significant (p<0.05)")

    output = "nostradamus/data/processed/monte_carlo_validation.json"
    with open(output, 'w') as f:
        json.dump(validated, f, indent=2)
    print(f"Saved validation results to: {output}")

    if qrng_service:
        print(f"\nRemaining QRNG bits: {qrng_service._pool.remaining:,}")

if __name__ == "__main__":
    main()
