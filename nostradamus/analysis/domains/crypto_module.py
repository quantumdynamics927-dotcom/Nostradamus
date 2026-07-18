#!/usr/bin/env python3
"""
Cryptography Module
Cipher detection, acrostic analysis, and cryptographic pattern analysis.
Based on research showing statistical anomalies in Nostradamus's text.
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter

# Acrostic Patterns
ACROSTIC_PATTERNS = [
    ("century_first_lines", "First letter of each quatrain in a century forms a word"),
    ("quatrain_first", "First letters of quatrains form a message"),
    ("diagonal", "Diagonal letters form hidden text"),
    ("last_letters", "Last letters form a hidden word"),
]

# Letter Groupings for Cipher Detection
CIPHER_INDICATORS = {
    "unusual_pairs": ["xz", "qx", "jx", "qz", "jq", "zx"],
    "high_value_letters": ["q", "x", "z", "j", "k"],
    "vowel_consonant_ratio": 0.4,  # French typically ~0.45
}

# Symbol Categories
SYMBOL_CATEGORIES = {
    "animals": ["lion", "loup", "serpent", "aigle", "corbeau", "ours", "lievre", "cheval", "boeuf"],
    "celestial": ["soleil", "lune", "astre", "etoile", "planete", "mars", "jupiter", "saturne"],
    "elements": ["feu", "eau", "terre", "air", "flamme", "pluie"],
    "metals": ["or", "argent", "fer", "bronze", "cuivre"],
    "colors": ["rouge", "blanc", "noir", "vert", "bleu", "jaune"],
    "directions": ["est", "ouest", "nord", "sud", "orient", "occident"],
}


@dataclass
class CryptographicProfile:
    """Cryptographic analysis of a quatrain."""
    quatrain_id: str
    acrostic_candidates: List[str]
    is_acrostic_strong: bool
    letter_anomaly_score: float
    cipher_probability: str
    symbol_encoding_zones: List[str]
    suspicious_patterns: List[str]

    def to_dict(self) -> Dict:
        return {
            "quatrain_id": self.quatrain_id,
            "acrostic_candidates": self.acrostic_candidates,
            "is_acrostic_strong": self.is_acrostic_strong,
            "letter_anomaly_score": self.letter_anomaly_score,
            "cipher_probability": self.cipher_probability,
            "symbol_encoding_zones": self.symbol_encoding_zones,
            "suspicious_patterns": self.suspicious_patterns
        }


class CryptoModule:
    """
    Analyze quatrains for cryptographic patterns.
    Implements research findings on statistical anomalies.
    """

    def __init__(self):
        self.french_freq = self._build_french_freq()
        self.symbol_map = SYMBOL_CATEGORIES

    def _build_french_freq(self) -> Dict[str, float]:
        """Expected French letter frequencies."""
        return {
            'e': 14.7, 'a': 8.2, 's': 7.9, 'i': 7.2, 't': 7.0,
            'n': 7.0, 'r': 6.5, 'l': 5.8, 'u': 5.8, 'o': 5.1,
            'd': 3.5, 'c': 3.3, 'p': 3.0, 'm': 2.8, 'f': 1.2,
            'b': 0.9, 'g': 0.8, 'h': 0.7, 'v': 0.6, 'y': 0.2,
            'x': 0.2, 'z': 0.1, 'j': 0.1, 'q': 0.1, 'k': 0.0
        }

    def extract_first_letters(self, text: str) -> str:
        """Extract first letter of each word."""
        words = text.split()
        return ''.join(w[0] for w in words if w and w[0].isalpha())

    def extract_last_letters(self, text: str) -> str:
        """Extract last letter of each word."""
        words = text.split()
        return ''.join(w[-1] if w[-1].isalpha() else '' for w in words if w)

    def check_acrostic(self, quatrains: List[Dict]) -> Dict:
        """
        Check if first letters of quatrains form hidden message.
        Works on a century (list of quatrains).
        """
        if not quatrains:
            return {"has_acrostic": False, "message": ""}

        # Get first letters
        first_letters = []
        for q in quatrains:
            fr = q.get("french", "")
            first = fr[0] if fr and fr[0].isalpha() else ''
            first_letters.append(first)

        acrostic = ''.join(first_letters).upper()

        # Look for recognizable patterns
        patterns_found = []

        # Check for Roman numerals (century structure)
        if re.match(r'^[IVXLCDM]+$', acrostic):
            patterns_found.append("Roman numeral sequence")

        # Check for word-like sequences
        word_pattern = re.findall(r'[A-Z]{4,}', acrostic)
        if word_pattern:
            patterns_found.extend(word_pattern[:3])

        return {
            "has_acrostic": len(patterns_found) > 0,
            "acrostic": acrostic,
            "patterns_found": patterns_found,
            "length": len(acrostic)
        }

    def check_acrostic_in_verse(self, text: str) -> List[str]:
        """
        Check for acrostic within a single quatrain's lines.
        Quatrains have 4 lines - check first letters.
        """
        # Split into lines (assume 4 lines)
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if len(lines) >= 4:
            first_letters = ''.join(l[0].upper() if l and l[0].isalpha() else '' for l in lines[:4])
            return [first_letters] if len(first_letters) == 4 else []
        return []

    def compute_letter_anomaly_score(self, text: str) -> float:
        """
        Compute how anomalous the letter distribution is.
        Returns 0-1, where 1 = highly anomalous (possible cipher).
        """
        text_clean = re.sub(r'[^a-z]', '', text.lower())
        if len(text_clean) < 10:
            return 0.0

        # Count frequencies
        freq = Counter(text_clean)
        total = len(text_clean)

        # Compute deviation from expected French
        deviations = []
        for letter, expected_pct in self.french_freq.items():
            observed = freq.get(letter, 0) / total * 100
            deviation = abs(observed - expected_pct) / (expected_pct + 0.1)
            deviations.append(deviation)

        # Average deviation
        avg_deviation = sum(deviations) / len(deviations)

        # Normalize to 0-1
        score = min(1.0, avg_deviation / 2)
        return round(score, 3)

    def detect_unusual_pairs(self, text: str) -> List[str]:
        """Find unusual letter pairs that might indicate cipher."""
        text_clean = re.sub(r'[^a-z]', '', text.lower())
        pairs = [text_clean[i:i+2] for i in range(len(text_clean)-1)]
        unusual = []

        for pair in set(pairs):
            if pair in CIPHER_INDICATORS["unusual_pairs"]:
                count = pairs.count(pair)
                unusual.append(f"{pair} appears {count}x")

        return unusual

    def check_symbol_encoding_zones(self, text: str) -> List[str]:
        """
        Identify zones where symbols might encode entities.
        Based on animal/metaphor clusters.
        """
        text_lower = text.lower()
        zones = []

        for category, keywords in self.symbol_map.items():
            matches = [kw for kw in keywords if kw in text_lower]
            if len(matches) >= 2:
                zones.append(f"{category}: {', '.join(matches)}")

        return zones

    def detect_suspicious_patterns(self, text: str) -> List[str]:
        """Find suspicious cryptographic patterns."""
        patterns = []
        text_lower = text.lower()

        # Check for repeated letters
        for letter in set(text_lower):
            count = text_lower.count(letter)
            if count >= 5 and count / len(text_lower) > 0.1:
                patterns.append(f"High '{letter}' frequency: {count}x")

        # Check for number-like sequences that could be coordinates
        numbers = re.findall(r'\d+', text)
        if len(numbers) >= 3:
            patterns.append(f"Multiple numbers: {numbers[:5]}")

        # Check for unusual word lengths
        words = text.split()
        long_words = [w for w in words if len(w) > 12]
        if len(long_words) > 2:
            patterns.append(f"Very long words: {len(long_words)} found")

        # Check for alternating patterns
        if len(text) > 20:
            cleaned = re.sub(r'[^a-z]', '', text_lower)
            if len(cleaned) > 10:
                for i in range(len(cleaned) - 4):
                    chunk = cleaned[i:i+3]
                    if cleaned[i:i+3] == cleaned[i+3:i+6]:
                        patterns.append(f"Repeating pattern: '{chunk}'")
                        break

        return patterns

    def run_chi_squared_test(self, text: str) -> Dict:
        """Run chi-squared test against French letter distribution."""
        text_clean = re.sub(r'[^a-z]', '', text.lower())
        if len(text_clean) < 20:
            return {"status": "text_too_short"}

        observed = Counter(text_clean)
        total = len(text_clean)

        chi_sq = 0
        for letter, expected_pct in self.french_freq.items():
            expected = expected_pct / 100 * total
            obs = observed.get(letter, 0)
            if expected > 0:
                chi_sq += ((obs - expected) ** 2) / expected

        return {
            "chi_squared": round(chi_sq, 2),
            "degrees_of_freedom": 24,
            "interpretation": "anomalous" if chi_sq > 35 else "normal",
            "p_approx": "low" if chi_sq > 35 else "high"
        }

    def index_of_coincidence(self, text: str) -> float:
        """
        Compute Index of Coincidence.
        French plaintext ~0.074, random ~0.0385, substitution cipher ~0.067.
        """
        text_clean = re.sub(r'[^a-z]', '', text.lower())
        if len(text_clean) < 2:
            return 0

        freq = Counter(text_clean)
        n = len(text_clean)

        ic = sum(f * (f - 1) for f in freq.values()) / (n * (n - 1))
        return round(ic, 6)

    def analyze(self, text: str, quatrain_id: str = "") -> CryptographicProfile:
        """
        Full cryptographic analysis of a quatrain.

        Returns CryptographicProfile with all findings.
        """
        first_letters = self.extract_first_letters(text)
        last_letters = self.extract_last_letters(text)
        anomaly_score = self.compute_letter_anomaly_score(text)
        unusual_pairs = self.detect_unusual_pairs(text)
        symbol_zones = self.check_symbol_encoding_zones(text)
        suspicious = self.detect_suspicious_patterns(text)
        ic = self.index_of_coincidence(text)
        chi_result = self.run_chi_squared_test(text)

        # Determine cipher probability
        cipher_prob = "low"
        if anomaly_score > 0.3 or chi_result.get("interpretation") == "anomalous":
            cipher_prob = "medium"
        if anomaly_score > 0.5 and unusual_pairs:
            cipher_prob = "high"

        # Check for strong acrostic candidates
        acrostics = []
        if len(first_letters) >= 4:
            acrostics.append(first_letters[:4])

        is_acrostic_strong = len(acrostics) > 0 and any(
            len(set(a)) >= 3 for a in acrostics
        )

        return CryptographicProfile(
            quatrain_id=quatrain_id,
            acrostic_candidates=acrostics,
            is_acrostic_strong=is_acrostic_strong,
            letter_anomaly_score=anomaly_score,
            cipher_probability=cipher_prob,
            symbol_encoding_zones=symbol_zones,
            suspicious_patterns=suspicious
        )


# Symbolic Encoding Analysis
class SymbolicEncoder:
    """
    Track how symbols might encode entities.
    Based on the theory that animal/metaphor clusters encode specific events/people.
    """

    def __init__(self):
        self.entity_symbols: Dict[str, List[str]] = {
            # Political entities
            "france": ["fleur", "lis", "gaulois", "franc"],
            "england": ["lion", "rosace", "albion"],
            "spain": ["dogue", "ibere", "castillac"],
            "holy_roman_empire": ["aigle", "imperial"],
            "ottoman": ["crescent", "turc", "sulta"],

            # Religious entities
            "church": ["croix", "tiare", "eveque"],
            "protestant": ["chapel", "reforme"],
            "jews": ["synagogue", "juif"],

            # Event types
            "war": ["guerrier", "armee", "bataille", "mars"],
            "plague": ["peste", "mort", "corbeau"],
            "famine": ["famine", "ble", "reve"],
            "flood": ["eau", "deluge", "inondation"],
        }

    def find_entity_clusters(self, text: str) -> List[str]:
        """Identify which entity clusters appear in text."""
        text_lower = text.lower()
        found = []

        for entity, symbols in self.entity_symbols.items():
            matches = sum(1 for s in symbols if s in text_lower)
            if matches >= 2:
                found.append(f"{entity} ({matches} symbols)")

        return found

    def encode_message(self, symbols: List[str]) -> str:
        """
        Given a sequence of symbols, suggest what entity they might encode.
        """
        # Simplified - real implementation would be more complex
        return "Symbolic encoding interpretation requires domain knowledge"
