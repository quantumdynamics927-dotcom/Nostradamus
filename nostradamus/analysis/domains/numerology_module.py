#!/usr/bin/env python3
"""
Numerology Module
Number patterns, cycles, gematria, and structural analysis.
"""

import re
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

# Sacred/Numerological Number Meanings
NUMBER_MEANINGS = {
    1: {"name": "Unity", "symbolism": "God, primacy, beginning"},
    2: {"name": "Duality", "symbolism": "Binary, opposition, balance"},
    3: {"name": "Trinity", "symbolism": "Divine perfection, Holy Trinity"},
    4: {"name": "Elements", "symbolism": "Four elements, earth, stability"},
    5: {"name": "Pentad", "symbolism": "Human senses, CHANGE"},
    6: {"name": "Hexad", "symbolism": "Work, completion"},
    7: {"name": "Heptad", "symbolism": "Sacred, seven sacraments, seven days"},
    8: {"name": "Octad", "symbolism": "Infinity, resurrection"},
    9: {"name": "Ennead", "symbolism": "Choir of angels, wisdom"},
    10: {"name": "Decad", "symbolism": "Commandments, decimal base"},
    11: {"name": "Hendecad", "symbolism": "Master number, spiritual insight"},
    12: {"name": "Duodecad", "symbolism": "Apostles, tribes, completeness"},
    13: {"name": "Triskaidecad", "symbolism": "Change, transformation"},
    14: {"name": "Tetradecad", "symbolism": "Two weeks, cycles"},
    15: {"name": "Quindecad", "symbolism": "Robert Fludd's mystical number"},
    20: {"name": "Scrupuli", "symbolism": "Twenty, Roman computation"},
    30: {"name": "Trente", "symbolism": "Thirty, age of Christ"},
    40: {"name": "Quarante", "symbolism": "Testing, fasting period"},
    50: {"name": "Jubilee", "symbolism": "Fifty, jubilee year"},
    100: {"name": "Century", "symbolism": "Hundred, hundredfold"},
    144: {"name": "Elect", "symbolism": "144,000 chosen in Revelation"},
    1000: {"name": "Millenium", "symbolism": "Thousand, eternal"},
}

# Cyclic Patterns in History
HISTORICAL_CYCLES = {
    7: {"name": "Seven Year Cycle", "description": "Agricultural, economic cycles"},
    10: {"name": "Decade", "description": "Decadal political cycles"},
    12: {"name": "Zodiac Cycle", "description": "Twelve year Jupiter cycle"},
    19: {"name": "Metonic Cycle", "description": "19 year lunar cycle"},
    28: {"name": "Solar Cycle", "description": "28 year solar calendar"},
    50: {"name": "Jubilee Cycle", "description": "Biblical 50-year cycle"},
    60: {"name": "Sexagesimal", "description": "Babylonian 60-year cycles"},
    100: {"name": "Centennial", "description": "Century cycles"},
}


@dataclass
class NumerologicalProfile:
    """Numerological analysis of a quatrain."""
    quatrain_id: str
    explicit_numbers: List[int]
    word_numbers: List[Tuple[str, int]]  # (word, value)
    gematria_sum: int
    significant_numbers: List[int]  # Numbers with sacred meaning
    cycle_references: List[str]  # Cycle names referenced
    structural_anomalies: List[str]  # Statistical anomalies
    is_number_heavy: bool

    def to_dict(self) -> Dict:
        return {
            "quatrain_id": self.quatrain_id,
            "explicit_numbers": self.explicit_numbers,
            "word_numbers": self.word_numbers,
            "gematria_sum": self.gematria_sum,
            "significant_numbers": self.significant_numbers,
            "cycle_references": self.cycle_references,
            "structural_anomalies": self.structural_anomalies,
            "is_number_heavy": self.is_number_heavy
        }


class NumerologyModule:
    """
    Analyze numerological patterns in quatrains.
    Includes gematria, number symbolism, and cycle detection.
    """

    def __init__(self):
        self.letter_values = self._build_gematria()

    def _build_gematria(self) -> Dict[str, int]:
        """
        Build French Elizabethan gematria (A=1, B=2, ... Z=26).
        Based on Renaissance computational methods.
        """
        return {chr(ord('a') + i): i + 1 for i in range(26)}

    def extract_explicit_numbers(self, text: str) -> List[int]:
        """Extract all explicit integer values from text."""
        # Arabic numerals
        numerals = [int(m) for m in re.findall(r'\b(\d+)\b', text)]

        # Roman numerals (I, V, X, L, C, D, M)
        roman_pattern = r'\b([IVXLCDM]+)\b'
        romans = re.findall(roman_pattern, text.upper())
        for r in romans:
            val = self._roman_to_int(r)
            if val > 0:
                numerals.append(val)

        # Word numbers
        word_nums = self._extract_word_numbers(text)
        numerals.extend(word_nums)

        return list(set(numerals))

    def _roman_to_int(self, s: str) -> int:
        """Convert Roman numeral to integer."""
        roman_vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        result = 0
        prev = 0
        for c in reversed(s):
            v = roman_vals.get(c, 0)
            if v < prev:
                result -= v
            else:
                result += v
            prev = v
        return result

    def _extract_word_numbers(self, text: str) -> List[int]:
        """Extract French number words."""
        text_lower = text.lower()
        numbers = []

        word_to_num = {
            'un': 1, 'une': 1, 'premier': 1, 'premiere': 1,
            'deux': 2, 'seconde': 2, 'second': 2,
            'trois': 3, 'tiers': 3, 'tierce': 3,
            'quatre': 4, 'quart': 4,
            'cinq': 5, 'cinquieme': 5,
            'six': 6, 'sixieme': 6,
            'sept': 7, 'septime': 7, 'septieme': 7,
            'huit': 8, 'huitieme': 8,
            'neuf': 9, 'neuvieme': 9,
            'dix': 10, 'dixieme': 10,
            'onz': 11, 'onzieme': 11,
            'douze': 12, 'douzieme': 12,
            'treize': 13, 'treizieme': 13,
            'quatorze': 14, 'quatorzieme': 14,
            'quinze': 15, 'quinzième': 15,
            'seize': 16,
            'vingt': 20, 'vingtieme': 20,
            'trente': 30,
            'quarante': 40,
            'cinquante': 50,
            'soixante': 60,
            'cent': 100, 'centaine': 100,
            'mille': 1000,
        }

        for word, val in word_to_num.items():
            if word in text_lower:
                numbers.append(val)

        return numbers

    def compute_gematria(self, text: str) -> int:
        """Compute simple gematria sum (A=1, B=2, ... Z=26)."""
        text_lower = re.sub(r'[^a-z]', '', text.lower())
        return sum(self.letter_values.get(c, 0) for c in text_lower)

    def find_significant_numbers(self, numbers: List[int]) -> List[int]:
        """Filter to numbers with special meaning."""
        return [n for n in set(numbers) if n in NUMBER_MEANINGS]

    def detect_cycle_references(self, text: str) -> List[str]:
        """Detect references to known historical/numerological cycles."""
        text_lower = text.lower()
        cycles = []

        for num, info in HISTORICAL_CYCLES.items():
            # Check for the number
            if str(num) in text or f" {num} " in text:
                cycles.append(f"{info['name']} ({num} years)")
            # Check for decade references
            if num == 10 and ('dix' in text_lower or 'decade' in text_lower):
                cycles.append(f"{info['name']}")
            # Check for century references
            if num == 100 and ('cent' in text_lower):
                cycles.append(f"{info['name']}")

        return cycles

    def analyze_structure(self, text: str) -> List[str]:
        """Detect structural anomalies in text."""
        anomalies = []

        # Check letter frequency anomalies
        text_lower = re.sub(r'[^a-z]', '', text.lower())
        if text_lower:
            freq = Counter(text_lower)
            most_common_char, count = freq.most_common(1)[0]
            total = sum(freq.values())
            ratio = count / total

            if ratio > 0.2:  # Same letter > 20%
                anomalies.append(f"High frequency: '{most_common_char}' = {ratio:.1%}")
            elif ratio < 0.01:
                anomalies.append(f"Low frequency: rare letters present")

        # Check word length distribution
        words = text.split()
        if words:
            lengths = [len(w) for w in words]
            avg = sum(lengths) / len(lengths)

            if avg > 8:
                anomalies.append(f"Long words average: {avg:.1f} chars")
            elif avg < 4:
                anomalies.append(f"Short words average: {avg:.1f} chars")

        # Check for repeated patterns
        if len(text) > 20:
            # Check for palindromes
            cleaned = re.sub(r'[^a-z]', '', text.lower())
            if cleaned == cleaned[::-1]:
                anomalies.append("Palindrome detected")

        return anomalies

    def is_number_heavy(self, text: str, threshold: float = 0.02) -> bool:
        """
        Determine if quatrain is unusually number-heavy.
        threshold: minimum ratio of digits to total chars.
        """
        digits = sum(c.isdigit() for c in text)
        return digits / len(text) > threshold if text else False

    def analyze(self, text: str, quatrain_id: str = "") -> NumerologicalProfile:
        """
        Full numerological analysis.

        Returns NumerologicalProfile with all findings.
        """
        explicit_nums = self.extract_explicit_numbers(text)
        word_nums = [(w, self._word_to_num(w)) for w in text.split()
                     if self._word_to_num(w) is not None]
        gematria = self.compute_gematria(text)
        significant = self.find_significant_numbers(explicit_nums)
        cycles = self.detect_cycle_references(text)
        anomalies = self.analyze_structure(text)
        number_heavy = self.is_number_heavy(text)

        return NumerologicalProfile(
            quatrain_id=quatrain_id,
            explicit_numbers=explicit_nums,
            word_numbers=word_nums,
            gematria_sum=gematria,
            significant_numbers=significant,
            cycle_references=cycles,
            structural_anomalies=anomalies,
            is_number_heavy=number_heavy
        )

    def _word_to_num(self, word: str) -> Optional[int]:
        """Convert word to number if it's a number word."""
        word_lower = word.lower().strip('.,;:!?')
        word_to_num = {
            'un': 1, 'une': 1, 'deux': 2, 'trois': 3, 'quatre': 4,
            'cinq': 5, 'six': 6, 'sept': 7, 'huit': 8, 'neuf': 9,
            'dix': 10, 'vingt': 20, 'trente': 30, 'quarante': 40,
            'cent': 100, 'mille': 1000,
        }
        return word_to_num.get(word_lower)


# Cipher Detection Utilities
class CipherDetector:
    """
    Statistical tests for possible cipher content.
    Based on research showing statistical anomalies in encoded text.
    """

    def __init__(self):
        self.english_freq = {
            'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0,
            'n': 6.7, 's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3,
            'l': 4.0, 'c': 2.8, 'u': 2.8, 'm': 2.4, 'w': 2.4,
            'f': 2.2, 'g': 2.0, 'y': 2.0, 'p': 1.9, 'b': 1.5,
            'v': 1.0, 'k': 0.8, 'j': 0.15, 'x': 0.15, 'q': 0.10,
            'z': 0.07
        }

    def letter_frequency_test(self, text: str) -> Dict:
        """
        Compute chi-squared deviation from expected letter frequencies.
        High chi-squared suggests possible cipher or substitution.
        """
        text_lower = re.sub(r'[^a-z]', '', text.lower())
        if len(text_lower) < 20:
            return {"status": "too_short", "chi_squared": 0}

        # Count frequencies
        observed = Counter(text_lower)
        total = len(text_lower)

        # Compute chi-squared
        chi_sq = 0
        for letter, expected_pct in self.english_freq.items():
            expected = expected_pct / 100 * total
            observed_count = observed.get(letter, 0)
            if expected > 0:
                chi_sq += ((observed_count - expected) ** 2) / expected

        return {
            "chi_squared": chi_sq,
            "status": "normal" if chi_sq < 50 else "anomalous",
            "interpretation": "Possible cipher" if chi_sq > 50 else "Normal text"
        }

    def index_of_coincidence(self, text: str) -> float:
        """
        Compute Index of Coincidence (IC).
        For English plaintext: ~0.0667
        For random text: ~0.0385
        High IC suggests simple substitution cipher.
        """
        text_lower = re.sub(r'[^a-z]', '', text.lower())
        if len(text_lower) < 2:
            return 0

        freq = Counter(text_lower)
        n = len(text_lower)

        ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
        return ic

    def detect_cipher_candidate(self, text: str) -> Dict:
        """
        Run multiple tests to determine if text might contain cipher.
        """
        ic = self.index_of_coincidence(text)
        freq_result = self.letter_frequency_test(text)

        # IC interpretation
        if ic > 0.07:
            ic_interp = "High IC - possible substitution cipher"
        elif ic > 0.05:
            ic_interp = "Elevated IC - could be simple substitution"
        else:
            ic_interp = "Normal IC - likely plaintext"

        return {
            "index_of_coincidence": ic,
            "ic_interpretation": ic_interp,
            "frequency_test": freq_result,
            "cipher_probability": "high" if freq_result["chi_squared"] > 50 or ic > 0.07 else "low"
        }
