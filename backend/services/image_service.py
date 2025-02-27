import os
import base64
import requests
import logging
import random
import time
from prompt_engineering.image_gen import get_image_prompt, CHARACTERS

logger = logging.getLogger(__name__)

class ImageService:
    # Available BFL FLUX models
    FLUX_MODELS = {
        "ultra": "https://api.us1.bfl.ai/v1/flux-pro-1.1-ultra",
        "standard": "https://api.us1.bfl.ai/v1/flux-pro-1.1",
        "fast": "https://api.us1.bfl.ai/v1/flux-pro-1.1-fast",
        "anime": "https://api.us1.bfl.ai/v1/flux-anime-1.1"
    }

    def get_reference_image(self, character_id):
        """Get base64 encoded reference image for character"""
        # Load directly from file
        try:
            # Standard path for character images
            filename = f"{character_id.capitalize()}.png"
            
            image_path = os.path.join(os.path.dirname(__file__), "..", "assets", filename)
            
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                    logger.info(f"Loaded reference image from file: {image_path}")
                    return base64.b64encode(image_bytes).decode('utf-8')
            else:
                logger.error(f"Image not found: {image_path}")
        except Exception as e:
            logger.error(f"Error loading reference image: {str(e)}")
        
        logger.warning(f"No reference image found for {character_id}")
        return None

    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.blackforestlabs.ai/v1/generate"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        self.model_type = "ultra"
        self.api_url = self.FLUX_MODELS.get(self.model_type, self.FLUX_MODELS["ultra"])
        # make empty envelope, BFL wants it this format
        self.api_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'x-key': api_key
        }
        self.generated_images = {}  # Cache of generated images by emotion

    def set_model(self, model_type: str):
        """Change FLUX model type"""
        if model_type in self.FLUX_MODELS:
            self.model_type = model_type
            self.api_url = self.FLUX_MODELS[model_type]
            logger.info(f"Switched to FLUX model: {model_type}")
        else:
            logger.error(f"Unknown FLUX model: {model_type}")

    def poll_for_image(self, polling_url):
        """ (letter content info):
        Context-Type: application/json will have the following data
        {
        'id': 'd7624f0e-cc8d-40eb-aab8-b65b07c1ef67', 
        'polling_url': 'https://api.us1.bfl.ai/v1/get_result?id=d7624f0e-cc8d-40eb-aab8-b65b07c1ef67'
        }
        """
        logger.info("Sending request to BFL-API")
        try:
            while True:
                time.sleep(0.5)
                result = requests.get(polling_url, headers=self.api_headers).json()
                
                if result.get("status") == 'Ready' and result.get('result', {}).get('sample'):
                    logger.info("Successfully received generated image")
                    return result['result']['sample']  # Actually return the URL!
                else:
                    logger.debug(f"Status: {result.get('status')}")
        except Exception as e:
            logger.error(f"Error polling for image: {str(e)}")
            return None

    def save_image_history(self, character_id, emotion, image_url):
        """Save generated image to history"""
        try:
            image_data = {
                "character": character_id,
                "emotion": emotion,
                "url": image_url,
                "timestamp": time.time()
            }
            self.memory_service.add_memory(f"image_history_{character_id}", image_data)
            logger.info(f"Saved image history for {character_id} with emotion {emotion}")
        except Exception as e:
            logger.error(f"Failed to save image history: {e}")

    def generate_image(self, body_language, character_id='nina'):
        """Generate character image with appropriate facial expression and body language"""
        try:
            # Get the final prompt directly from emotion dict
            prompt = body_language.get('final_prompt')
            
            # Fallback if no prompt was provided
            if not prompt:
                logger.warning(f"No prompt provided for {character_id}, using default")
                # Use the proper prompt generator with character info
                prompt = get_image_prompt(character_id, {"expression": "neutral", "gesture": "relaxed"})
            
            # Ensure character is centered in the image
            prompt = f"{prompt} Character positioned precisely in the center of the frame. Symmetrical composition. Head and shoulders centered."
            
            # Get reference image
            reference_image = self.get_reference_image(character_id)
            
            # If no cached image, generate new one
            logger.info(f"Generating image for {character_id} with prompt: {prompt[:100]}...")
            
            # For debugging - let's see the full request
            request_data = {
                "prompt": prompt,
                "negative_prompt": "deformed, ugly, bad anatomy",
                "guidance_scale": 7.5,
                "width": 512,
                "height": 512
            }
            
            # Add reference image if available
            if reference_image:
                request_data.update({
                    "reference_image": reference_image,
                    "reference_weight": 0.8,  # Higher weight for more consistency
                    "seed": random.randint(1, 10000)
                })
            
            logger.info(f"Request data: {request_data}")
            logger.info(f"API URL: {self.api_url}")
            logger.info(f"Headers: {self.api_headers}")
            
            response = requests.post(
                self.api_url,
                headers=self.api_headers,
                json=request_data
            )
    
            if response.status_code == 200:
                image_data = response.json()
                logger.info(f"BFL API JSON Response: {image_data}")
                
                # The response doesn't contain the image URL directly
                # Instead it contains a polling URL we need to check
                polling_url = image_data.get("polling_url")
                if polling_url:
                    logger.info(f"Polling for image at: {polling_url}")
                    image_url = self.poll_for_image(polling_url)
                    logger.info(f"Retrieved final image URL: {image_url}")
                    return image_url
                else:
                    logger.error("No polling URL received")
                    return None
            else:
                logger.error(f"Image generation failed with status {response.status_code}: {response.text}")
                # Fallback to default images if API fails
                if character_id == "harold":
                    return "https://example.com/default_harold.jpg"  # Replace with actual URL
                else:
                    return "https://example.com/default_nina.jpg"    # Replace with actual URL
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            return None
