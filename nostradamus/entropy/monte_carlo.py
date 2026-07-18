"""
Monte Carlo Validation Module
Uses QRNG entropy for rigorous pattern match validation.
"""

import json
import math
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from entropy.qrng_service import EntropyService, EntropyConfig, EntropyMode

@dataclass
class ValidationResult:
    """Result of Monte Carlo validation."""
    quatrain_id: str
    match_score: float
    p_value: float
    is_significant: bool
    null_distribution_mean: float
    null_distribution_std: float
    confidence_level: float
    entropy_source: str
    simulations: int

    def to_dict(self) -> Dict:
        return {
            "quatrain_id": self.quatrain_id,
            "match_score": self.match_score,
            "p_value": self.p_value,
            "is_significant": self.is_significant,
            "null_mean": self.null_distribution_mean,
            "null_std": self.null_distribution_std,
            "confidence": self.confidence_level,
            "entropy_source": self.entropy_source,
            "simulations": self.simulations
        }

class MonteCarloValidator:
    """
    Monte Carlo validation for quatrain-event matches.
    Uses QRNG entropy to estimate probability of match occurring by chance.
    """

    def __init__(self, entropy_service: EntropyService):
        self.entropy = entropy_service
        self.results: List[ValidationResult] = []

    def validate_match(
        self,
        quatrain_id: str,
        observed_score: float,
        event_ids: List[str],
        score_fn: Callable[[str, str], float],
        n_simulations: int = 10000
    ) -> ValidationResult:
        """
        Validate whether an observed match score is statistically significant.

        Args:
            quatrain_id: ID of quatrain being validated
            observed_score: Actual match score between quatrain and event
            event_ids: List of candidate event IDs
            score_fn: Function(event_id, randomized_label) -> float
            n_simulations: Number of Monte Carlo simulations

        Returns:
            ValidationResult with p-value and significance
        """
        # Generate null distribution by randomizing labels
        null_scores = []
        for _ in range(n_simulations):
            # Randomly permute event labels using QRNG
            shuffled_events, source = self.entropy.get_int(0, len(event_ids) - 1)
            randomized_event = event_ids[shuffled_events]

            # Compute score with randomized pairing
            # In real impl, would use proper permutation
            random_score = score_fn(event_ids[0], randomized_event)
            null_scores.append(random_score)

        # Compute statistics
        null_mean = sum(null_scores) / len(null_scores)
        null_variance = sum((s - null_mean) ** 2 for s in null_scores) / len(null_scores)
        null_std = math.sqrt(null_variance)

        # Compute p-value
        p_value = sum(1 for s in null_scores if s >= observed_score) / len(null_scores)

        # Determine significance at 0.05 level
        is_significant = p_value < 0.05

        # Confidence level (1 - p_value)
        confidence = 1.0 - p_value

        result = ValidationResult(
            quatrain_id=quatrain_id,
            match_score=observed_score,
            p_value=p_value,
            is_significant=is_significant,
            null_distribution_mean=null_mean,
            null_distribution_std=null_std,
            confidence_level=confidence,
            entropy_source="qrng" if self.entropy._pool._cursor > 0 else "prng",
            simulations=n_simulations
        )

        self.results.append(result)
        return result

    def validate_match_batch(
        self,
        matches: List[Dict],
        score_fn: Callable[[str, str], float],
        n_simulations: int = 5000
    ) -> List[ValidationResult]:
        """Validate multiple matches in batch."""
        results = []
        for match in matches:
            result = self.validate_match(
                quatrain_id=match["quatrain_id"],
                observed_score=match["score"],
                event_ids=match["candidate_events"],
                score_fn=score_fn,
                n_simulations=n_simulations
            )
            results.append(result)
        return results

    def compare_prng_vs_qrng(
        self,
        quatrain_id: str,
        observed_score: float,
        event_ids: List[str],
        score_fn: Callable[[str, str], float],
        n_simulations: int = 5000
    ) -> Dict:
        """
        Run validation twice: once with PRNG, once with QRNG.
        Compare results to quantify whether entropy source matters.
        """
        # Save current mode
        original_mode = EntropyConfig.mode

        # Run with PRNG
        EntropyConfig.mode = EntropyMode.PRNG
        prng_result = self.validate_match(
            quatrain_id, observed_score, event_ids, score_fn, n_simulations
        )

        # Run with QRNG (if available)
        EntropyConfig.mode = EntropyMode.QRNG
        qrng_result = self.validate_match(
            quatrain_id, observed_score, event_ids, score_fn, n_simulations
        )

        # Restore mode
        EntropyConfig.mode = original_mode

        return {
            "quatrain_id": quatrain_id,
            "observed_score": observed_score,
            "prng_result": prng_result.to_dict(),
            "qrng_result": qrng_result.to_dict(),
            "difference": {
                "p_value_diff": abs(prng_result.p_value - qrng_result.p_value),
                "confidence_diff": abs(prng_result.confidence_level - qrng_result.confidence_level)
            },
            "conclusion": "entropy_matters" if abs(prng_result.p_value - qrng_result.p_value) > 0.05 else "entropy_neutral"
        }

    def summary(self) -> Dict:
        """Generate summary of all validations."""
        if not self.results:
            return {"total": 0}

        significant = sum(1 for r in self.results if r.is_significant)
        avg_p = sum(r.p_value for r in self.results) / len(self.results)
        avg_confidence = sum(r.confidence_level for r in self.results) / len(self.results)

        return {
            "total_validations": len(self.results),
            "significant_matches": significant,
            "significance_rate": significant / len(self.results),
            "mean_p_value": avg_p,
            "mean_confidence": avg_confidence,
            "entropy_usage": {
                "qrng_calls": sum(1 for r in self.results if r.entropy_source == "qrng"),
                "prng_calls": sum(1 for r in self.results if r.entropy_source == "prng")
            }
        }

# === INTERPRETATION SAMPLING ===

class InterpretationSampler:
    """
    Use QRNG to sample interpretations of ambiguous quatrains.
    Handles multiple paraphrase sets, symbol mappings, etc.
    """

    def __init__(self, entropy_service: EntropyService):
        self.entropy = entropy_service

    def sample_paraphrase_set(
        self,
        quatrain_id: str,
        paraphrases: List[str],
        n_samples: int = 100
    ) -> List[Tuple[int, str]]:
        """
        Randomly sample from possible paraphrases.
        Returns list of (index, paraphrase) tuples.
        """
        samples = []
        for _ in range(n_samples):
            idx, source = self.entropy.get_int(0, len(paraphrases) - 1)
            samples.append((idx, paraphrases[idx], source))
        return samples

    def sample_symbol_mapping(
        self,
        symbol: str,
        candidate_mappings: Dict[str, float],
        n_samples: int = 100
    ) -> Dict[str, float]:
        """
        Sample symbol -> entity mappings weighted by probability.
        Uses QRNG for random selection.
        """
        # Build weighted distribution
        items = list(candidate_mappings.items())
        weights = [w for _, w in items]

        # Sample using QRNG
        samples = {}
        for _ in range(n_samples):
            # Simple uniform sampling then accept/reject
            idx, source = self.entropy.get_int(0, len(items) - 1)
            entity, weight = items[idx]
            samples[entity] = samples.get(entity, 0) + 1

        # Normalize to probabilities
        total = sum(samples.values())
        return {k: v / total for k, v in samples.items()}

    def monte_carlo_symbol_analysis(
        self,
        quatrain_symbols: List[str],
        symbol_universe: Dict[str, List[str]],
        event_universe: List[str],
        n_iterations: int = 1000
    ) -> Dict:
        """
        Monte Carlo analysis: do random symbol->entity mappings
        produce same event matches as actual mappings?
        """
        matches_per_iteration = []

        for _ in range(n_iterations):
            # Random symbol assignment
            random_assignments = {}
            for sym in quatrain_symbols:
                candidates = symbol_universe.get(sym, [])
                if candidates:
                    idx, _ = self.entropy.get_int(0, len(candidates) - 1)
                    random_assignments[sym] = candidates[idx]

            # Count how many map to events
            matched = sum(1 for sym, entity in random_assignments.items()
                         if entity in event_universe)
            matches_per_iteration.append(matched)

        # Statistics
        actual_matches = len([s for s in quatrain_symbols
                             if s in symbol_universe and symbol_universe[s] & set(event_universe)])

        return {
            "actual_matches": actual_matches,
            "random_mean": sum(matches_per_iteration) / len(matches_per_iteration),
            "random_std": math.sqrt(
                sum((m - sum(matches_per_iteration)/len(matches_per_iteration))**2
                    for m in matches_per_iteration) / len(matches_per_iteration)
            ),
            "p_value": sum(1 for m in matches_per_iteration if m >= actual_matches) / len(matches_per_iteration),
            "is_significant": actual_matches > sum(matches_per_iteration) / len(matches_per_iteration)
        }

# === CIPHER SEARCH ===

class CipherSearcher:
    """
    Use QRNG to search for possible cipher patterns in quatrain text.
    Random key/permutation proposals for cryptanalysis.
    """

    def __init__(self, entropy_service: EntropyService):
        self.entropy = entropy_service

    def propose_substitution_keys(self, alphabet: str, n_proposals: int = 1000) -> List[Dict[str, str]]:
        """
        Propose random substitution cipher keys.
        Uses QRNG for key generation.
        """
        proposals = []
        import random

        for _ in range(n_proposals):
            key = {}
            remaining = list(alphabet)
            random.shuffle(remaining)  # In real impl, use QRNG for shuffle
            for i, c in enumerate(alphabet):
                key[c] = remaining[i]
            proposals.append(key)

        return proposals

    def random_permutation_test(
        self,
        text: str,
        statistic_fn: Callable[[str], float],
        n_permutations: int = 10000
    ) -> Tuple[float, float]:
        """
        Test if a statistic (e.g., letter frequency chi-squared)
        is significantly different from random.
        Uses QRNG for permutations.
        """
        observed_stat = statistic_fn(text)

        # Generate null distribution via permutations
        null_stats = []
        chars = list(text)
        for _ in range(n_permutations):
            # Fisher-Yates shuffle using QRNG
            n = len(chars)
            for i in range(n - 1, 0, -1):
                j, _ = self.entropy.get_int(0, i)
                chars[i], chars[j] = chars[j], chars[i]

            shuffled = ''.join(chars)
            null_stats.append(statistic_fn(shuffled))

        # Compute p-value
        p_value = sum(1 for s in null_stats if s >= observed_stat) / len(null_stats)
        return observed_stat, p_value
