import os
import base64
import logging
from prompt_engineering.image_gen import get_image_prompt

logger = logging.getLogger(__name__)

class ImageService:
    # Available BFL FLUX models
    FLUX_MODELS = {
        "ultra": "https://api.us1.bfl.ai/v1/flux-pro-1.1-ultra",
        "standard": "https://api.us1.bfl.ai/v1/flux-pro-1.1",
        "fast": "https://api.us1.bfl.ai/v1/flux-pro-1.1-fast",
        "anime": "https://api.us1.bfl.ai/v1/flux-anime-1.1"
    }

    def __init__(self, api_key):
        self.api_key = api_key
        self.api_headers = {
            'Content-Type': 'application/json',
            'x-key': api_key
        }

    def get_reference_image(self, character_id):
        """Get base64 encoded reference image for character"""
        # Load directly from file
        try:
            # get the image from the assets folder
            filename = f"{character_id.capitalize()}.png"
            image_path = os.path.join(os.path.dirname(__file__), "..", "assets", filename)
            
            # Check if the file exists
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                    return base64.b64encode(image_bytes).decode('utf-8')
            else:
                logger.error(f"Image not found: {image_path}")
        except Exception as e:
            logger.error(f"Error loading reference image: {str(e)}")
        
        logger.warning(f"No reference image found for {character_id}")
        return None

    def generate_image(self, body_language_desc, character_id='nina'):
        """Return actual image data"""
        logger.info(f"Image generation requested for {character_id}")
        
        # Get the base64 encoded image directly
        image_data = self.get_reference_image(character_id)
        
        if image_data:
            # Return with data URI format that can be used directly in <img> tags
            return f"data:image/png;base64,{image_data}"
        else:
            # Fallback if image not found
            logger.error(f"Failed to load image for {character_id}")
            return "https://example.com/default_nina.jpg"
