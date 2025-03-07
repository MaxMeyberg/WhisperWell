import logging
from typing import Dict, Optional
from openai import OpenAI
from prompt_engineering.personalities import get_personality_prompt, get_appearance_prompt
from prompt_engineering.image_gen import get_image_prompt

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.allChatHistory = {}  # Local memory only
        
    def get_ai_response(self, chatHistory) -> Optional[str]:
        """Get response from OpenAI based on chat history"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-0125-preview",  # GPT-4 Turbo
                messages=chatHistory
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI response error: {str(e)}")
            return f"Error: {str(e)}"
            
    def analyze_body_language(self, chatHistory, character_id) -> str:
        """Analyzes chat to return text description of appropriate body language"""
        
        # Get character description from personalities.py
        character_desc = get_appearance_prompt(character_id)
        
        # Create body language analysis prompt using character description
        system_content = f"""
            You are analyzing a conversation to determine {character_desc['name']}'s appropriate facial expression and body language.
            
            IMPORTANT: You are analyzing specifically as {character_desc['name']}, not as any other character.
            The response should reflect how {character_desc['name']} would express themselves in this conversation.
            
            {character_desc['appearance']}
            
            Provide a paragraph describing the body language how {character_desc['name']} would appear in this moment of conversation.
            Focus on facial expressions, posture, and subtle body language cues.
        """

        emotion_prompt = [
            {"role": "system", "content": system_content},
            *chatHistory
        ]
        
        try:
            response = self.get_ai_response(emotion_prompt)
            return response  # Just return the text analysis directly
        except Exception as e:
            logger.error(f"Error in analyze_body_language: {e}")
            return f"Default {character_id} expression: neutral, attentive posture with subtle nod of understanding."

    def handle_chat(self, currMessage, sessionId, character_id, user_face = None):
        """Main chat handling method"""
        try:
            # Create a character-specific session ID to maintain separate histories
            character_session_id = f"{sessionId}_{character_id}"


            if character_session_id not in self.allChatHistory:
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
                #get personality from the prompt.py
                systemPrompt = get_personality_prompt(character_id)
                self.allChatHistory[character_session_id] = [
                    {"role": "system", "content": systemPrompt}
                ]
                # register the chat history for this current talk
                chatHistory = self.allChatHistory[character_session_id]

            #adds face recognition if enabled 
            if user_face:
                emotion_message = {
                    "role": "system", 
                    "content": f"The user appears to be feeling {user_face.get('emotion')} (confidence: {user_face.get('confidence', 0):.2f}). Take this into account in your response."
                }
                self.allChatHistory[character_session_id].append(emotion_message)
            # send chatHistory to OPEN AI w get_ai_response
            
            # FIX: Add user message BEFORE getting AI response
            self.allChatHistory[character_session_id].append(
                {"role": "user", "content": currMessage}
            )
            
            # Make sure chatHistory is up to date
            chatHistory = self.allChatHistory[character_session_id]
            
            # Get AI response AFTER adding user message
            aiResponse = self.get_ai_response(chatHistory)
            
            # Add AI response to chat history
            chatHistory.append(
                {"role": "assistant", "content": aiResponse}
            )
            
            # Get body language description as text
            body_language_text = self.analyze_body_language(chatHistory, character_id)
            print("Body Language Analysis:", body_language_text)
            
            # Return all needed information
            return aiResponse, chatHistory, body_language_text
            
        except Exception as e:
            logger.error(f"Chat handling error: {str(e)}")
            return None, None, None
