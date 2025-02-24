from typing import Dict, Optional
from .ai_utils import get_ai_response #allows for GPT API calls
import logging #allows us to log into console

""" what is __name__ ? (click for more info)
__name__ is a special Python variable that contains:

For example, in ai_utils.py it would be "nina_thought_process.ai_utils"
For example, in emotional_iq.py it would be "nina_thought_process.emotional_iq"
For example, in personality.py it would be "nina_thought_process.personality"

TLDR: the directory but using .s instead of /s
"""
""" what is getLogger? (click for more info)
logger = logging.getLogger(__name__) #confirms we can log 

logger is a special object that:
Shows which file the log came from
Helps track where errors/messages originate
Can be configured with different levels (debug, info, warning, error)
"""

logger = logging.getLogger(__name__) #confirms we can log 

def analyze_emotional_context(chatHistory) -> Dict[str, str]:
    """
    End Game TODO: Add in stuff like reall bad trauam like murder, grape, etc.
    Analyzes chat and returns emotion details for image generation
    """
    
    emotion_prompt = [
        {"role": "system", "content": """
            You are Nina analyzing a conversation. Determine the emotional context and describe how you should appear.
            Format your response EXACTLY as:
            EMOTION: [single word emotion]
            EXPRESSION: [facial expression details]
            GESTURE: [body language details]
            Keep descriptions natural and subtle - no exaggerated expressions.
            """},
        *chatHistory
    ]
    
    response = get_ai_response(emotion_prompt)
    print("Nina in emotional IQ: ", response)
    
    # Parse response into dict
    lines = response.split('\n')
    emotion_dict = {}
    for line in lines:
        if 'EXPRESSION:' in line:
            emotion_dict['expression'] = line.split('EXPRESSION:')[1].strip()
        elif 'GESTURE:' in line:
            emotion_dict['gesture'] = line.split('GESTURE:')[1].strip()
    
    return emotion_dict
