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

__all__ = [
    'analyze_text', 'calculate_ambiguity_index',
    'infer_astrological_config',
    'extract_entities', 'extract_event_type', 'match_to_events',
    'validate_prediction', 'PERIOD_SOURCES'
]
