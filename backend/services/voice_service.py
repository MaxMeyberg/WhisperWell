import logging
import requests
import os
from typing import Optional
import base64
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.elevenlabs.io/v1/text-to-speech"
        # Add multiple voice IDs for characters
        self.voice_ids = {
            "nina": "21m00Tcm4TlvDq8ikWAM",  # Replace with actual voice ID for Nina
            "harold": "pNInz6obpgDQGcFmaJgB"  # Replace with actual elderly male voice ID
        }
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }

    def generate_speech(self, text, character_id):
        """Generate speech from text using ElevenLabs API"""
        try:
            # Add validation for environment variables
            if not self.api_key:
                logger.error("Missing ELEVENLABS_API_KEY environment variable")
                return None
                
            if not self.voice_id:
                logger.error("Missing ELEVENLABS_VOICE_ID environment variable")
                return None

            """ (click for more deets)
            --------------------------------[CONCEPT]--------------------------------
            We need to follow ElevenLabs API format:

            # 1. Headers - Authentication and format
            headers = {
                'Accept': 'audio/mpeg',           # What format we want back
                'Content-Type': 'application/json',# What format we're sending
                'xi-api-key': self.api_key        # Our authentication
            }

            # 2. Voice Settings - How Nina should sound
            voice_settings = {
                "stability": 0.5,        # How consistent the voice should be
                "similarity_boost": 0.75, # How much to match the original voice
                "style": 0.5,            # Speaking style variation
                "speaking_rate": 1.3     # How fast Nina talks
            }

            # 3. Request Body - What Nina should say
            data = {
                "text": "I understand how you're feeling...",
                "model_id": "eleven_monolingual_v1",
                "voice_settings": voice_settings
            }

            # 4. How audio is handled:
            In app.py:
            audioData = None
            if voiceEnabled:
                audioData = voice_service.generate_speech(ninaResponse)  # Get binary audio
                if audioData:
                    audioData = base64.b64encode(audioData).decode('utf-8')  # Convert to base64 for frontend
            --------------------------------[EXAMPLE]--------------------------------

            The flow:
            1. Frontend enables voice
            2. Nina's text response gets sent here
            3. ElevenLabs converts text to speech
            4. Audio bytes get sent back to frontend
            5. Frontend plays the audio
            """

            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}/stream"
            
            headers = {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': self.api_key
            }
            
            # Add text validation
            if not text or len(text.strip()) == 0:
                logger.error("Empty text provided")
                return None
                
            # Add text length limit (ElevenLabs has a limit)
            if len(text) > 5000:
                logger.warning("Text too long, truncating to 5000 characters")
                text = text[:5000]
            voice_id = self.voice_ids.get(character_id, self.voice_ids["nina"])
            data = {
                "voice_id": voice_id,
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.71,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
            }

            logger.info(f"Sending request to ElevenLabs API with text length: {len(text)}")
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            
            if response.ok:
                logger.info("Successfully generated speech")
                if not response.content:
                    logger.error("Received empty response content")
                    return None
                audio = response.content
                return audio
            else:
                logger.error(f"Speech generation failed: Status {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
                
        except requests.Timeout:
            logger.error("Request to ElevenLabs API timed out")
            return None
        except requests.ConnectionError:
            logger.error("Connection error to ElevenLabs API")
            return None
        except Exception as e:
            logger.error(f"Speech generation error: {str(e)}")
            return None
