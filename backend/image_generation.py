import os
import time
import requests
import base64
from typing import Dict, Optional
import logging
import random
import time

logger = logging.getLogger(__name__)

BFL_API_KEY = os.getenv("BLACK_FOREST_API_KEY")
BFL_API_URLS = { 'flux-pro-1.1-ultra': 'https://api.us1.bfl.ai/v1/flux-pro-1.1-ultra',
                 'flux-pro-1.1': 'https://api.us1.bfl.ai/v1/flux-pro-1.1',
                 'flux-pro': 'https://api.us1.bfl.ai/v1/flux-pro',
                 'flux-dev': 'https://api.us1.bfl.ai/v1/flux-dev'}
BFL_API_URL = BFL_API_URLS['flux-pro-1.1-ultra']

REFERENCE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets/Therapist-F-Smile.png")

#DONE: checks to see if image is ready
def poll_for_image(polling_url):
  
    """ (letter content info):
    Context-Type: application/json will have the following data
    {
    'id': 'd7624f0e-cc8d-40eb-aab8-b65b07c1ef67', 
    'polling_url': 'https://api.us1.bfl.ai/v1/get_result?id=d7624f0e-cc8d-40eb-aab8-b65b07c1ef67'
    }
    """
    # make empty envalope, BFL wants it this format
    api_headers = {
        'accept': 'application/json',
        'x-key': BFL_API_KEY
    }
    logger.info("Sending request to BFL-API")
    try:
        while True:
            time.sleep(0.5)
            result = requests.get(polling_url, headers=api_headers).json()
            
            if result.get("status") == 'Ready' and result.get('result', {}).get('sample'):
                logger.info("Successfully received generated image")
                return result['result']['sample']  # Actually return the URL!
            else:
                logger.debug(f"Status: {result.get('status')}")
                
    except Exception as e:
        logger.error(f"Error polling for image: {str(e)}")
        return None





# #TODO: generate image rewrite
# def generate_image(emotion: str, client=None) -> Optional[str]:
#     """Generate image based on emotional state using Black Forest Labs"""

#     print("Image will generate on the following prompt:", emotion)
#     try:
#         if client is None:
#             raise ValueError("OpenAI client not provided")
        
#         # Read and encode reference image
#         try:
#             with open(REFERENCE_IMAGE_PATH, 'rb') as f:
#                 image_bytes = f.read()
#                 reference_image = base64.b64encode(image_bytes).decode('utf-8')
#                 logger.info(f"Successfully loaded reference image from {REFERENCE_IMAGE_PATH}")
#         except Exception as e:
#             logger.error(f"Failed to load reference image: {str(e)}")
#             return None
        
#         # Add randomization to ensure unique generations
#         random_seed = random.randint(1, 10000)
        
#         params = {
#             "prompt": f"""Match reference image exactly, changing only facial expression and subtle body language:
            
#              Base Appearance (maintain these exactly):
#             - Brown shoulder-length bob cut with side-swept bangs
#             - Large hazel eyes
#             - Heart-shaped face
#             - Dark grey blazer over cream blouse
#             - Professional office background

#             Current Emotional Expression: {emotion}
            
#             Important:
#             - Focus on natural, authentic emotional expression
#             - Maintain professional demeanor while showing genuine emotion
#             - Clean anime style with clear emotional reading
#             - Keep same art style, character design, and environment as reference
#             - Maintain exact same clothing, hair, and background
#             - Change ONLY facial expression and body language to match emotion
#             """,
#             "width": 1024,
#             "height": 1024,
#             "prompt_upsampling": False,
#             "seed": random_seed,
#             "safety_tolerance": 2,
#             "output_format": "jpeg",
#             "reference_image": reference_image,
#             "reference_weight": 0.80 # Balanced value
#         }

#         headers = {
#             'Content-Type': 'application/json',
#             'X-Key': BFL_API_KEY
#         }

#         logger.info(f"Sending request to BFL API for emotion: {emotion} with seed: {random_seed}")
#         #change image quality here:
#         response = requests.post(BFL_API_URL, json=params, headers=headers)
        
#         if not response.ok:
#             logger.error(f"BFL API request failed: Status {response.status_code}")
#             logger.error(f"Response: {response.text}")
#             return None

#         data = response.json()
#         logger.info(f"BFL API response: {data}")

#         polling_url = data.get('polling_url')
#         if not polling_url:
#             logger.error("No polling URL received")
#             return None

#         return poll_for_image(polling_url)

#     except Exception as e:
#         logger.error(f"Image generation error: {str(e)}")
#         return None
    

def generate_image(emotion):
    
    # check if the emotion is None
    if emotion == None:
        logger.error("Nina is not feeling anything from GPT")
        return None
    """ (api_headers structure)
    ENVELOPE (Headers):
    To: BFL API Server
    From: Our Application
    Type: JSON Document
    Authentication: Our API Key

    LETTER CONTENT (Body):
    {
        actual data here...
    }
    """

    # make empty envalope, BFL wants it this format
    api_headers = {
        'accept': 'application/json',
        'x-key': BFL_API_KEY
    }

    #check to make sure the API to BFL is working, requets is used to make http requests
    BFL_check = requests.post(BFL_API_URL, 
                            headers=api_headers,
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
        """CHECKPOINT: MANUALY CODE FROM HERE"""
        # Read and encode reference image
        with open(REFERENCE_IMAGE_PATH, 'rb') as f:
            image_bytes = f.read()
            reference_image = base64.b64encode(image_bytes).decode('utf-8')
            logger.info("Successfully loaded reference image")
    except Exception as e:
        logger.error(f"Failed to load reference image: {str(e)}")
        return None

    # Add randomization to ensure unique generations
    random_seed = random.randint(1, 10000)
    
    # Get just the filename from REFERENCE_IMAGE_PATH
    nina_default_pic = os.path.basename(REFERENCE_IMAGE_PATH)  # "Therapist-F-Smile.png"

    params = {
        "prompt": f"""Match reference image exactly, changing only facial expression and subtle body language:
        
        Base Appearance (maintain exactly):
        - Soft, youthful face with rosy cheeks and natural makeup
        - Medium-length dark brown bob with wispy side bangs
        - Large bright hzael eyes with long lashes
        - Small nose and gentle smile with pink lips
        - Black blazer over high-neck cream ribbed sweater
        - Professional office with bookshelves in background
        - Gold stud earrings
        - Warm, soft lighting from left side

        Current Emotional Expression: {emotion}
        
        Important:
        - Keep anime-style art with clean lines and soft shading
        - Maintain exact facial structure and proportions
        - Preserve the warm, inviting expression
        - Keep professional yet approachable demeanor
        - Maintain same lighting and composition
        - Change ONLY emotional expression while keeping core features
        """,
        "width": 1024,
        "height": 1024,
        "prompt_upsampling": False,
        "seed": random_seed,
        "safety_tolerance": 2,
        "output_format": "jpeg",
        "reference_image": reference_image,
        "reference_weight": 0.80  # Keep strong reference
    }

    headers = {
        'Content-Type': 'application/json',
        'X-Key': BFL_API_KEY
    }

    logger.info(f"Sending request to BFL API for emotion: {emotion} with seed: {random_seed}")
    #change image quality here:
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

    