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

def analyze_emotional_context(chatHistory) -> str:
    """
    End Game TODO: Add in stuff like reall bad trauam like murder, grape, etc.
    emotionMap is ranked by priority, so trauma is highest priority
    """
    
    emotion_prompt = [
        {"role": "system", "content": "You are a companion named Nina, and you are given a conversation between a user and you. Analyze the conversation and determine the most emotional context for the user's message. explain the emotion and body language in great detail as this will be used to generate an image. Use Dark Triad Psychology to determine the emotion."},
        *chatHistory #the * is for Chat GPT to like the format and look at the recent chat history (remove the system part)
    ]
    emotion = get_ai_response(emotion_prompt)
    print("Nina in emotional IQ: ", emotion)
    return emotion
  