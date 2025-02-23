# Import main functions to make them easily accessible
from .ai_utils import get_ai_response
from .emotional_iq import analyze_emotional_context
from .personality import nina_personality

# You can optionally specify which functions should be available when someone imports *
__all__ = [
    'get_ai_response',
    'analyze_emotional_context',
    'nina_personality'
]