import os
import base64
import requests
import logging
import random
import time
from prompt_engineering.image_gen import get_image_prompt, CHARACTERS

logger = logging.getLogger(__name__)

class ImageService:
    def __init__(self, api_key, memory_service):
        self.api_key = api_key
        self.memory_service = memory_service  # For storing image history
        self.api_url = "https://api.us1.bfl.ai/v1/flux-pro-1.1-ultra"
        # make empty envelope, BFL wants it this format
        self.api_headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
            'x-key': api_key
        }
        self.generated_images = {}  # Cache of generated images by emotion

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

    def generate_image(self, emotion, character_id='nina'):
        # Try cache first
        cache_key = f"{character_id}_{emotion}"
        if cache_key in self.generated_images:
            return self.generated_images[cache_key]
            
        # Generate if not in cache
        image_url = self._generate_new_image(emotion, character_id)
        if image_url:
            self.generated_images[cache_key] = image_url
            self.save_image_history(character_id, emotion, image_url)
        return image_url

    def _generate_new_image(self, emotion, character_id='nina'):
        """Generate image based on emotional state using Black Forest Labs"""
        # check if the emotion is None
        if emotion is None:
            logger.error("Nina is not feeling anything from GPT")
            return None

        # Get reference image path
        ref_path = os.path.join(os.path.dirname(__file__), 
                               "..", 
                               CHARACTERS[character_id]["image_path"])

        #check to make sure the API to BFL is working, requests is used to make http requests
        BFL_check = requests.post(self.api_url, 
                                headers=self.api_headers,
                                json={
                                    "prompt": "test",
                                    "width": 512,
                                    "height": 512
                                })  # Minimal required fields
        
        #fail safe is the BFL API is working or not
        if not BFL_check.ok:
            logger.error(f"BFL API ain't working (Status code): {BFL_check.status_code}")
            return None

        #incase we get a corrupt file, we have "try"
        try:
            """CHECKPOINT: MANUALLY CODE FROM HERE"""
            # Read and encode reference image
            with open(ref_path, 'rb') as f:
                image_bytes = f.read()
                reference_image = base64.b64encode(image_bytes).decode('utf-8')
                logger.info("Image Generation Success")
        except Exception as e:
            logger.error(f"Image Generation Failed: {str(e)}")
            return None

        # Add randomization to ensure unique generations
        random_seed = random.randint(1, 10000)

        #Prompt Engineering for Nina, we need to change this later.
        params = {
            "prompt": get_image_prompt(character_id, emotion),
            "width": 1024,
            "height": 1024,
            "prompt_upsampling": False,
            "seed": random_seed,
            "safety_tolerance": 2,
            "output_format": "jpeg",
            "reference_image": reference_image,
            "reference_weight": 0.80  # Keep strong reference
        }

        logger.info(f"Sending request to BFL API for emotion: {emotion} with seed: {random_seed}")
        #change image quality here:
        response = requests.post(self.api_url, json=params, headers=self.api_headers)
        
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

        return self.poll_for_image(polling_url)
