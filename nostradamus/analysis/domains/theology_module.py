#!/usr/bin/env python3
"""
Theology & Esoterica Module
Biblical motifs, religious symbolism, occult references in Nostradamus.
"""

import re
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass

# Religious & Biblical References
BIBLICAL_SYMBOLS = {
    "dieu": {"type": "divine", "meaning": "God", "context": "monotheism"},
    "jesus": {"type": "christ", "meaning": "Jesus Christ", "context": "christian"},
    "christ": {"type": "christ", "meaning": "Christ", "context": "christian"},
    "esprit": {"type": "holy_spirit", "meaning": "Holy Spirit", "context": "trinity"},
    "sainte": {"type": "saint", "meaning": "Holy/Saint", "context": "christian"},
    "ange": {"type": "angelic", "meaning": "Angel", "context": "heavenly"},
    "demon": {"type": "demonic", "meaning": "Demon", "context": "occult"},
    "diable": {"type": "demonic", "meaning": "Devil", "context": "occult"},
    "lucifer": {"type": "demonic", "meaning": "Lucifer", "context": "occult"},
    "bible": {"type": "scripture", "meaning": "Bible", "context": "christian"},
    "eveque": {"type": "clerical", "meaning": "Bishop", "context": "christian"},
    "pape": {"type": "clerical", "meaning": "Pope", "context": "christian"},
    "cardinal": {"type": "clerical", "meaning": "Cardinal", "context": "christian"},
    "temple": {"type": "sacred_space", "meaning": "Temple", "context": "universal"},
    "eglise": {"type": "sacred_space", "meaning": "Church", "context": "christian"},
    "secte": {"type": "religious_group", "meaning": "Sect", "context": "religious"},
    "heretique": {"type": "religious_group", "meaning": "Heretic", "context": "christian"},
    "idol": {"type": "pagan", "meaning": "Idol", "context": "pagan"},
    "sacrifice": {"type": "ritual", "meaning": "Sacrifice", "context": "universal"},
    "prophete": {"type": "divine", "meaning": "Prophet", "context": "revelation"},
}

# Apocalyptic & Esoteric Symbols
APOCALYPTIC_SYMBOLS = {
    "bete": {"type": "apocalyptic", "meaning": "The Beast", "context": "revelation"},
    "antechrist": {"type": "apocalyptic", "meaning": "Antichrist", "context": "revelation"},
    "apocalypse": {"type": "apocalyptic", "meaning": "Apocalypse", "context": "revelation"},
    "fin": {"type": "eschatological", "meaning": "The End", "context": "time"},
    "dernier": {"type": "eschatological", "meaning": "Last/Final", "context": "time"},
    "jugement": {"type": "eschatological", "meaning": "Judgment", "context": "revelation"},
    "saint": {"type": "holy", "meaning": "Holy/Saint", "context": "christian"},
    "elu": {"type": "divine", "meaning": "The Chosen", "context": "election"},
    "elu": {"type": "divine", "meaning": "The Chosen", "context": "election"},
}

# Occult & Hermetic Symbols
OCCULT_SYMBOLS = {
    "magie": {"type": "occult", "meaning": "Magic", "context": "hermetic"},
    "sorcier": {"type": "occult", "meaning": "Sorcerer", "context": "witchcraft"},
    "enchanteur": {"type": "occult", "meaning": "Enchanter", "context": "magic"},
    "astrologie": {"type": "occult", "meaning": "Astrology", "context": "celestial"},
    "alchimie": {"type": "hermetic", "meaning": "Alchemy", "context": "transformation"},
    "kabale": {"type": "jewish_mysticism", "meaning": "Kabbalah", "context": "jewish"},
    "cabale": {"type": "jewish_mysticism", "meaning": "Kabbalah", "context": "jewish"},
    "tarot": {"type": "divination", "meaning": "Tarot", "context": "cartomancy"},
    "orne": {"type": "symbolic", "meaning": "Elm tree", "context": "sacred_tree"},
    "olivier": {"type": "symbolic", "meaning": "Olive", "context": "peace"},
    "chene": {"type": "symbolic", "meaning": "Oak", "context": "strength"},
}

# Numerological Sacred Numbers
SACRED_NUMBERS = {
    1: {"meaning": "Unity", "significance": "One God, primacy"},
    3: {"meaning": "Trinity", "significance": "Holy Trinity, divine perfection"},
    4: {"meaning": "Elements", "significance": "Four elements, earthly completeness"},
    7: {"meaning": "Sacred", "significance": "Seven sacraments, days of creation"},
    9: {"meaning": "Choir", "significance": "Nine choirs of angels"},
    10: {"meaning": "Commandments", "significance": "Ten Commandments, decimal base"},
    12: {"meaning": "Apostles", "significance": "Twelve Apostles, tribes of Israel"},
    40: {"meaning": "Testing", "significance": "Days of fasting, testing period"},
    144: {"meaning": "Elect", "significance": "144,000 chosen in Revelation"},
}


@dataclass
class TheologicalProfile:
    """Theological and esoteric profile of a quatrain."""
    quatrain_id: str
    biblical_references: List[str]
    apocalyptic_indicators: List[str]
    occult_symbols: List[str]
    numerological_numbers: List[int]
    sacred_geometry_hints: List[str]
    eschatology_score: float  # 0-1 scale of apocalyptic content
    hermetic_score: float     # 0-1 scale of hermetic/occult content
    clerical_score: float     # 0-1 scale of church/papal references

    def to_dict(self) -> Dict:
        return {
            "quatrain_id": self.quatrain_id,
            "biblical_references": self.biblical_references,
            "apocalyptic_indicators": self.apocalyptic_indicators,
            "occult_symbols": self.occult_symbols,
            "numerological_numbers": self.numerological_numbers,
            "sacred_geometry_hints": self.sacred_geometry_hints,
            "eschatology_score": self.eschatology_score,
            "hermetic_score": self.hermetic_score,
            "clerical_score": self.clerical_score
        }


class TheologyModule:
    """
    Analyze theological, biblical, and esoteric content in quatrains.
    Tracks apocalyptic themes, occult symbols, and numerological patterns.
    """

    def __init__(self):
        self.all_symbols = {**BIBLICAL_SYMBOLS, **APOCALYPTIC_SYMBOLS, **OCCULT_SYMBOLS}

    def extract_biblical_references(self, text: str) -> List[str]:
        """Find all biblical/religious references in text."""
        text_lower = text.lower()
        found = []

        for keyword, info in BIBLICAL_SYMBOLS.items():
            if keyword in text_lower:
                found.append(f"{keyword} ({info['meaning']})")

        return list(set(found))

    def extract_apocalyptic_indicators(self, text: str) -> List[str]:
        """Find apocalyptic and eschatological references."""
        text_lower = text.lower()
        found = []

        for keyword, info in APOCALYPTIC_SYMBOLS.items():
            if keyword in text_lower:
                found.append(f"{keyword} ({info['meaning']})")

        return list(set(found))

    def extract_occult_symbols(self, text: str) -> List[str]:
        """Find hermetic, occult, and esoteric symbols."""
        text_lower = text.lower()
        found = []

        for keyword, info in OCCULT_SYMBOLS.items():
            if keyword in text_lower:
                found.append(f"{keyword} ({info['meaning']})")

        return list(set(found))

    def extract_numerological_numbers(self, text: str) -> List[int]:
        """Extract significant numbers and their meanings."""
        numbers_found = []

        # Look for explicit numbers
        number_patterns = [
            r'\b(\d+)\b',  # Regular integers
            r'\b(sept|septime)\b',  # Seven
            r'\b(trois|tierce|tiers)\b',  # Three
            r'\b(douze|douziesme)\b',  # Twelve
            r'\b(quarante)\b',  # Forty
            r'\b(cent|centiesme)\b',  # Hundred
            r'\b(mille|milliesme)\b',  # Thousand
        ]

        text_lower = text.lower()

        for pattern in number_patterns:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                if isinstance(m, str):
                    # Convert word to number
                    word_to_num = {
                        'sept': 7, 'septime': 7,
                        'trois': 3, 'tierce': 3, 'tiers': 3,
                        'douze': 12, 'douziesme': 12,
                        'quarante': 40,
                        'cent': 100, 'centiesme': 100,
                        'mille': 1000, 'milliesme': 1000
                    }
                    num = word_to_num.get(m, None)
                    if num:
                        numbers_found.append(num)
                else:
                    numbers_found.append(int(m))

        # Check for sacred numbers and add their meanings
        sacred = []
        for num in numbers_found:
            if num in SACRED_NUMBERS:
                sacred.append(num)

        return list(set(sacred))

    def detect_sacred_geometry(self, text: str) -> List[str]:
        """Detect references to sacred geometry concepts."""
        hints = []
        text_lower = text.lower()

        # Circle, center, radius
        if any(w in text_lower for w in ['cercle', 'circle', 'centre', 'center', 'rayon', 'radius']):
            hints.append("circle/center symbolism")

        # Triangle
        if any(w in text_lower for w in ['trois', 'triangle', 'triangulaire']):
            hints.append("triangle symbolism")

        # Cross
        if any(w in text_lower for w in ['croix', 'cross', 'crucifix']):
            hints.append("cross symbolism")

        # Star/pentagram
        if any(w in text_lower for w in ['etoile', 'star', 'astre', 'pentagramme']):
            hints.append("star/celestial geometry")

        return hints

    def compute_eschatology_score(self, text: str) -> float:
        """
        Compute 0-1 score of apocalyptic/eschatological content.
        Based on density of apocalyptic keywords.
        """
        text_lower = text.lower()
        total_words = len(text_lower.split())

        apocalyptic_keywords = [
            'fin', 'dernier', 'jugement', 'apocalypse', 'bete', 'antechrist',
            'dieu', 'christ', 'esprit', 'saint', 'elu', 'predestined',
            'demon', 'diable', 'enfer', 'paradis', 'damnation', 'salvation'
        ]

        count = sum(1 for kw in apocalyptic_keywords if kw in text_lower)
        return min(1.0, count / 5)  # Normalize to 0-1

    def compute_hermetic_score(self, text: str) -> float:
        """
        Compute 0-1 score of hermetic/occult content.
        """
        text_lower = text.lower()

        hermetic_keywords = [
            'magie', 'sorcier', 'enchanteur', 'astrologie', 'alchimie',
            'kabale', 'cabale', 'tarot', 'orne', 'chene', 'olivier',
            'magique', 'occulte', 'hermetique', 'influence celeste'
        ]

        count = sum(1 for kw in hermetic_keywords if kw in text_lower)
        return min(1.0, count / 4)

    def compute_clerical_score(self, text: str) -> float:
        """
        Compute 0-1 score of clerical/papal references.
        """
        text_lower = text.lower()

        clerical_keywords = [
            'pape', 'papal', 'eveque', 'cardinal', 'eglise', 'temple',
            'religieux', 'religieux', 'chretiente', 'christol', 'chrestien',
            'heretique', 'secte', 'inquisition'
        ]

        count = sum(1 for kw in clerical_keywords if kw in text_lower)
        return min(1.0, count / 4)

    def analyze(self, text: str, quatrain_id: str = "") -> TheologicalProfile:
        """
        Full theological and esoteric analysis of a quatrain.

        Returns TheologicalProfile with all findings.
        """
        biblical = self.extract_biblical_references(text)
        apocalyptic = self.extract_apocalyptic_indicators(text)
        occult = self.extract_occult_symbols(text)
        numbers = self.extract_numerological_numbers(text)
        geometry = self.detect_sacred_geometry(text)

        eschatology = self.compute_eschatology_score(text)
        hermetic = self.compute_hermetic_score(text)
        clerical = self.compute_clerical_score(text)

        return TheologicalProfile(
            quatrain_id=quatrain_id,
            biblical_references=biblical,
            apocalyptic_indicators=apocalyptic,
            occult_symbols=occult,
            numerological_numbers=numbers,
            sacred_geometry_hints=geometry,
            eschatology_score=eschatology,
            hermetic_score=hermetic,
            clerical_score=clerical
        )


# Corpus-level statistics
def compute_theology_corpus_stats(profiles: List[TheologicalProfile]) -> Dict:
    """Compute statistics across a corpus of theological profiles."""

    total = len(profiles)
    if total == 0:
        return {}

    return {
        "total_quatrains": total,
        "avg_eschatology": sum(p.eschatology_score for p in profiles) / total,
        "avg_hermetic": sum(p.hermetic_score for p in profiles) / total,
        "avg_clerical": sum(p.clerical_score for p in profiles) / total,
        "high_apocalyptic": sum(1 for p in profiles if p.eschatology_score > 0.5),
        "high_occult": sum(1 for p in profiles if p.hermetic_score > 0.5),
        "most_common_biblical": _most_common([ref for p in profiles for ref in p.biblical_references]),
        "most_common_occult": _most_common([sym for p in profiles for sym in p.occult_symbols]),
        "numerology_distribution": _number_distribution(profiles)
    }


def _most_common(items: List[str], top_n: int = 10) -> List[Tuple[str, int]]:
    from collections import Counter
    return Counter(items).most_common(top_n)


def _number_distribution(profiles: List[TheologicalProfile]) -> Dict:
    from collections import Counter
    all_numbers = [n for p in profiles for n in p.numerological_numbers]
    return dict(Counter(all_numbers).most_common())
