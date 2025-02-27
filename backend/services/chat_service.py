import logging
from typing import Dict, Optional
import openai
from prompt_engineering.personalities import get_personality_prompt, get_personality_description
from prompt_engineering.image_gen import get_image_prompt

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.allChatHistory = {}  # Local memory only
        
    def get_ai_response(self, chatHistory) -> Optional[str]:
        """Get response from OpenAI based on chat history"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",  # GPT-4 Turbo
                messages=chatHistory
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"AI response error: {str(e)}")
            return f"Error: {str(e)}"

    def analyze_body_language(self, chatHistory, character_id) -> Dict[str, str]:
        """Analyzes chat to determine appropriate body language and expressions"""
        
        # Get character description from personalities.py
        character_desc = get_personality_description(character_id)
        
        # Create body language analysis prompt using character description
        system_content = f"""
            You are analyzing a conversation to determine {character_desc['name']}'s appropriate facial expression and body language.
            
            IMPORTANT: You are analyzing specifically as {character_desc['name']}, not as any other character.
            The response should reflect how {character_desc['name']} would express themselves in this conversation.
            
            {character_desc['appearance']}
            
            Format your response EXACTLY as:
            CONVERSATIONAL CONTEXT: [Brief analysis of the conversation's tone]
            
            IMAGE PROMPT FOR BLACK FOREST LABS:
            - Expression: [Description of facial expression - {character_desc['expression_style']}]
            - Eyes: [Eye expression - {character_desc['eye_style']}]
            - Mouth: [Mouth position - {character_desc['mouth_style']}]
            - Eyebrows: [Eyebrow position - {character_desc['eyebrow_style']}]
            - Head Position: [Any slight tilts or turns - {character_desc['head_style']}]
            - Body Language: [Posture - {character_desc['body_style']}]
            
            {character_desc['name']}'s expressions convey {character_desc['expression_summary']}.
        """

        emotion_prompt = [
            {"role": "system", "content": system_content},
            *chatHistory
        ]
        
        try:
            response = self.get_ai_response(emotion_prompt)
            print("Emotional Analysis:", response)  # For debugging
            
            # Parse response into dict for image generation
            lines = response.split('\n')
            emotion_dict = {}
            current_section = None
            
            for line in lines:
                if 'Expression:' in line:
                    emotion_dict['expression'] = line.split('Expression:')[1].strip()
                elif 'Body Language:' in line:
                    emotion_dict['gesture'] = line.split('Body Language:')[1].strip()
            
            # Generate final image prompt here
            final_prompt = get_image_prompt(character_id, emotion_dict)
            emotion_dict['final_prompt'] = final_prompt
            
            return emotion_dict
        except Exception as e:
            logger.error(f"Error in analyze_emotional_context: {e}")
            
            return {'final_prompt': f"Default {character_id} expression, neutral pose"}

    def handle_chat(self, currMessage, sessionId, character_id):
        """Main chat handling method"""
        try:
            # Create a character-specific session ID to maintain separate histories
            character_session_id = f"{sessionId}_{character_id}"
            
            if character_session_id not in self.allChatHistory:
                #get personality from the prompt.py
                systemPrompt = get_personality_prompt(character_id)
                self.allChatHistory[character_session_id] = [
                    {"role": "system", "content": systemPrompt}
                ]
            
            # Register chat History 
            self.allChatHistory[character_session_id].append(
                {"role": "user", "content": currMessage}
            )
            # register the chat history for this current talk
            chatHistory = self.allChatHistory[character_session_id]
            
            # send chatHistory to OPEN AI w get_ai_response
            aiResponse = self.get_ai_response(chatHistory)
            
            # add nina's response to the chat history
            chatHistory.append(
                {"role": "assistant", "content": aiResponse}
            )
            
            # No external saving needed - already in memory
            
            return aiResponse, chatHistory
            
        except Exception as e:
            logger.error(f"Chat handling error: {str(e)}")
            return None, None
