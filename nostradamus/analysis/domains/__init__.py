"""
Nostradamus Expert System - Domain Modules
Unified exports for all 8 expert domains.
"""

from .linguistics_module import analyze_text, calculate_ambiguity_index
from .astrology_module import infer_astrological_config
from .history_module import (
    extract_entities, extract_event_type, match_to_events,
    validate_prediction, PERIOD_SOURCES
)
from .theology_module import TheologyModule, compute_theology_corpus_stats
from .numerology_module import NumerologyModule, CipherDetector
from .crypto_module import CryptoModule, SymbolicEncoder
from .disaster_space_module import (
    DisasterProfile, SpaceProfile,
    analyze_disaster_space, analyze_disaster, analyze_space,
    get_catalog_stats
)

__all__ = [
    # Core
    'analyze_text', 'calculate_ambiguity_index',
    'infer_astrological_config',
    'extract_entities', 'extract_event_type', 'match_to_events',
    'validate_prediction', 'PERIOD_SOURCES',
    # New
    'TheologyModule', 'compute_theology_corpus_stats',
    'NumerologyModule', 'CipherDetector',
    'CryptoModule', 'SymbolicEncoder',
    # Disaster & Space
    'DisasterProfile', 'SpaceProfile',
    'analyze_disaster_space', 'analyze_disaster', 'analyze_space',
    'get_catalog_stats',
]
