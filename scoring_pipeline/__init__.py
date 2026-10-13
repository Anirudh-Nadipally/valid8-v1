# Valid8 Scoring Pipeline
# Deterministic scoring engine with 4 layers

from .pipeline import ScoringPipeline
from .extractor import Extractor
from .validator import Validator
from .scorer import Scorer
from .presenter import Presenter

# V4: Pattern-based classification
from .archetypes import ARCHETYPES, NEEDS_MORE_DATA, get_archetype, get_conviction_display
from .classifier import classify_archetype, extract_signals_from_extracted_data, ClassificationResult
from .grounding import GroundingService, enrich_idea_sync, grounding_result_to_dict

__all__ = [
    # V3 scoring
    'ScoringPipeline', 'Extractor', 'Validator', 'Scorer', 'Presenter',
    # V4 pattern classification
    'ARCHETYPES', 'NEEDS_MORE_DATA', 'get_archetype', 'get_conviction_display',
    'classify_archetype', 'extract_signals_from_extracted_data', 'ClassificationResult',
    'GroundingService', 'enrich_idea_sync', 'grounding_result_to_dict'
]
__version__ = '4.0.0'

