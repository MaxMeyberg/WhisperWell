import os
import base64
import logging
from prompt_engineering.image_gen import get_image_prompt
import http.client

logger = logging.getLogger(__name__)
"""
import http.client

conn = http.client.HTTPSConnection("api.us1.bfl.ai")

conn.request("GET", "/v1/get_result")

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))

"""
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
        print("We got to reference image")
        # Load directly from file
        try:
            #see which character we are using:
            if character_id == "Nina":
                filename = "Nina.png"
            elif character_id == "Harold":
                filename = "Harold.png"
            else:
                raise ValueError(f"Invalid character ID: {character_id}")
            
            image_path = os.path.join(os.path.dirname(__file__), "..", "assets", filename)
            print(f"Looking for image at: {image_path}")
            # Check if the file exists
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                    return base64.b64encode(image_bytes).decode('utf-8')
            else:
                logger.error(f"Image not found: {image_path}")
                return None
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

    def generate_image(self, body_language_desc, character_id='Nina'):
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
