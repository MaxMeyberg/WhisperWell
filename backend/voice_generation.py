import os
import requests
from typing import Optional
import logging
import base64
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

ELEVEN_LABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
THERAPIST_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

def generate_speech(text: str) -> Optional[bytes]:
    """Generate speech from text using ElevenLabs API"""
    try:
        # Add validation for environment variables
        if not ELEVEN_LABS_API_KEY:
            logger.error("Missing ELEVENLABS_API_KEY environment variable")
            return None
            
        if not THERAPIST_VOICE_ID:
            logger.error("Missing ELEVENLABS_VOICE_ID environment variable")
            return None

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{THERAPIST_VOICE_ID}/stream"
        
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': ELEVEN_LABS_API_KEY
        }
        
        # Add text validation
        if not text or len(text.strip()) == 0:
            logger.error("Empty text provided")
            return None
            
        # Add text length limit (ElevenLabs has a limit)
        if len(text) > 5000:
            logger.warning("Text too long, truncating to 5000 characters")
            text = text[:5000]
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.5,
                "speaking_rate": 1.3  # Adjusted speaking rate
            }
        }

        logger.info(f"Sending request to ElevenLabs API with text length: {len(text)}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.ok:
            logger.info("Successfully generated speech")
            if not response.content:
                logger.error("Received empty response content")
                return None
            return response.content
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