import os
import time
import requests
import base64
from typing import Dict, Optional
import logging
import random

logger = logging.getLogger(__name__)

BFL_API_KEY = os.getenv("BLACK_FOREST_API_KEY")
BFL_API_URL = 'https://api.us1.bfl.ai/v1/flux-pro-1.1'
REFERENCE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets/Therapist-F-Smile.png")

def get_emotion_details(emotion: str) -> Dict[str, str]:
    """Get detailed emotion descriptions"""
    emotion_map = {
        'sad': {
            'expression': 'gentle empathy with soft downturned eyes, compassionate smile',
            'gesture': 'head tilted to the side with a slight forward lean, one hand slightly raised in a supportive gesture',
            'intensity': 'subtle'
        },
        'angry': {
            'expression': 'calm and grounding presence with a composed smile, steady reassuring gaze',
            'gesture': 'sitting upright with shoulders back, hands folded calmly, slight forward lean to show engagement',
            'intensity': 'moderate'
        },
        'happy': {
            'expression': 'radiant warm smile with bright engaged eyes, slightly raised eyebrows',
            'gesture': 'animated head tilt with open body language, shoulders relaxed, one hand gesturing warmly',
            'intensity': 'moderate'
        },
        'anxious': {
            'expression': 'calming and reassuring expression with gentle eyes, soft understanding smile',
            'gesture': 'stable grounding presence, head tilted slightly forward, hands positioned to show openness and support',
            'intensity': 'subtle'
        },
        'neutral': {
            'expression': 'professional warmth with attentive eyes, gentle authentic smile',
            'gesture': 'balanced welcoming posture, subtle head tilt, hands resting naturally to convey openness',
            'intensity': 'subtle'
        }
    }
    return emotion_map.get(emotion, emotion_map['neutral'])

def poll_for_image(polling_url: str, max_attempts: int = 60, delay_ms: int = 2000) -> Optional[str]:
    """Poll for generated image"""
    headers = {
        'Content-Type': 'application/json',
        'X-Key': BFL_API_KEY
    }

    logger.info(f"Starting to poll: {polling_url}")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(polling_url, headers=headers)
            data = response.json()
            
            if attempt % 5 == 0:  # Log every 5th attempt
                logger.info(f"Poll attempt {attempt + 1}: {data}")

            if data.get('status') == 'Ready' and data.get('result', {}).get('sample'):
                logger.info("Successfully received generated image")
                return data['result']['sample']
                
            elif data.get('status') == 'Failed':
                logger.error(f"Image generation failed: {data.get('details')}")
                return None
                
            time.sleep(delay_ms / 1000)
            
        except Exception as e:
            logger.error(f"Polling error: {str(e)}")
            continue

    logger.error("Polling timed out")
    return None

def generate_therapist_image(emotion: str) -> Optional[str]:
    """Generate image based on emotional state using Black Forest Labs"""
    try:
        emotion_details = get_emotion_details(emotion)
        
        # Read and encode reference image
        try:
            with open(REFERENCE_IMAGE_PATH, 'rb') as f:
                image_bytes = f.read()
                reference_image = base64.b64encode(image_bytes).decode('utf-8')
                logger.info(f"Successfully loaded reference image from {REFERENCE_IMAGE_PATH}")
        except Exception as e:
            logger.error(f"Failed to load reference image: {str(e)}")
            return None
        
        # Add randomization to ensure unique generations
        random_seed = random.randint(1, 10000)
        
        params = {
            "prompt": f"""Match reference image exactly, changing only facial expression and subtle body language:
            
             Base Appearance (maintain these exactly):
            - Brown shoulder-length bob cut with side-swept bangs
            - Large hazel eyes
            - Heart-shaped face
            - Dark grey blazer over cream blouse
            - Professional office background

            Current Emotional Expression:
            - {emotion_details['expression']}
            - {emotion_details['gesture']}
            
            Important:
            - Focus on natural, authentic emotional expression
            - Maintain professional demeanor while showing genuine emotion
            - Clean anime style with clear emotional reading
            - Keep same art style, character design, and environment as reference
            - Maintain exact same clothing, hair, and background
            - Change ONLY: 
                * Facial expression: {emotion_details['expression']}
                * Body language: {emotion_details['gesture']}
            """,
            "width": 1024,
            "height": 1024,
            "prompt_upsampling": False,
            "seed": random_seed,
            "safety_tolerance": 2,
            "output_format": "jpeg",
            "reference_image": reference_image,
            "reference_weight": 0.80 # Balanced value
        }

        headers = {
            'Content-Type': 'application/json',
            'X-Key': BFL_API_KEY
        }

        logger.info(f"Sending request to BFL API for emotion: {emotion} with seed: {random_seed}")
        response = requests.post(BFL_API_URL, json=params, headers=headers)
        
        if not response.ok:
            logger.error(f"BFL API request failed: Status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

        data = response.json()
        logger.info(f"BFL API response: {data}")

        polling_url = data.get('polling_url')
        if not polling_url:
            logger.error("No polling URL received")
            return None

        return poll_for_image(polling_url)

    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        return None