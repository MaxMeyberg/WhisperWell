import logging
from typing import Dict, Optional
from openai import OpenAI
from prompt_engineering.personalities import get_personality_prompt

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, api_key, memory_service):
        self.client = OpenAI(api_key=api_key)
        self.memory_service = memory_service
        self.allChatHistory = {}  # Still keep in memory for quick access
        
    def get_ai_response(self, chatHistory, client=None) -> Optional[str]:
        """Get response from OpenAI based on chat history"""
        try:
            if client is None:
                raise ValueError("OpenAI client not provided")
                
            response = client.chat.completions.create(
                model="gpt-4-0125-preview",  # GPT-4 Turbo
                messages=chatHistory
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI response error: {str(e)}")
            return f"Error: {str(e)}"

    def analyze_emotional_context(self, chatHistory) -> Dict[str, str]:
        """
        End Game TODO: Add in stuff like really bad trauma like murder, grape, etc.
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
        
        #Nina wont run without the try/except
        try:
            response = self.get_ai_response(emotion_prompt, client=self.client)
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
        except Exception as e:
            logger.error(f"Error in analyze_emotional_context: {e}")
            return {}

    def handle_chat(self, currMessage, sessionId, voiceEnabled=False):
        """Main chat handling method"""
        try:
            #A new session w Nina, runs this
            if sessionId not in self.allChatHistory:
                #get Nina's personality from the prompt.py
                systemPrompt = get_personality_prompt('nina')
                """ (click for more deets)
                --------------------------------[CONCEPT]--------------------------------
                We need to follow OPEN AI's API format, for GPT to read it

                # 1. "system" - Instructions or context for the AI
                {
                    "role": "system",
                    "content": "You are Nina, a 21-year-old therapist..."
                }

                # 2. "user" - What the human says
                {
                    "role": "user", 
                    "content": "I feel sad today"
                }

                # 3. "assistant" - What Nina (AI) says
                {
                    "role": "assistant",
                    "content": "I understand how you're feeling..."
                }
                --------------------------------[EXAMPLE]--------------------------------

                Pattern in allChatHistory[sessionId]:
                [
                    {"role": "system", "content": get_personality_prompt('nina')},
                    {"role": "user", "content": "I feel sad today"},
                    {"role": "assistant", "content": "I hear you..."},
                    {"role": "user", "content": "my parrot died"},
                    {"role": "assistant", "content": "Awww, it hurts to lose a pet. I recently lost my hamster..."},
                ]
                """
                self.allChatHistory[sessionId] = [
                    {"role": "system", "content": systemPrompt}
                ]
            
            # Register chat History 
            self.allChatHistory[sessionId].append(
                {"role": "user", "content": currMessage}
            )
            # register the chat history for this current talk with Nina
            chatHistory = self.allChatHistory[sessionId]
            
            # send chatHistory to OPEN AI w get_ai_response
            ninaResponse = self.get_ai_response(chatHistory, client=self.client)
            
            # add nina's response to the chat history
            chatHistory.append(
                {"role": "assistant", "content": ninaResponse}
            )
            
            # Save to persistent storage after updating
            self.memory_service.save_chat_history(sessionId, chatHistory)
            
            return ninaResponse, chatHistory
            
        except Exception as e:
            logger.error(f"Chat handling error: {str(e)}")
            return None, None
