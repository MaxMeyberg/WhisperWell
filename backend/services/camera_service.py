import logging
import cv2
import base64
import io
import numpy as np
from deepface import DeepFace
from PIL import Image
import json  # Add this for helper functions

# Get the dedicated camera logger
logger = logging.getLogger('camera_service')

class CameraService:
    def __init__(self):
        self.previous_emotion = None
        self.confidence_threshold = 0.5  # Minimum confidence to report emotion
        
    def decode_base64_image(self, base64_string):
        """Convert base64 image to numpy array"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
                
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to numpy array (for OpenCV)
            return np.array(image)
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return None
    
    def _convert_numpy_types(self, obj):
        """Helper method to convert numpy types to Python native types"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj
        
    def detect_face(self, image_data):
        """Detect emotion from image data (base64 string)"""
        try:
            # Convert base64 to image
            if isinstance(image_data, str):
                image = self.decode_base64_image(image_data)
            else:
                image = image_data
                
            if image is None:
                return None
                
            # Analyze emotion
            result = DeepFace.analyze(
                img_path=image, 
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            # Get dominant emotion and score
            dominant_emotion = result[0]['dominant_emotion']
            emotion_scores = result[0]['emotion']
            confidence = emotion_scores[dominant_emotion]
            
            # Only return emotion if confidence is high enough
            if confidence >= self.confidence_threshold:
                self.previous_emotion = dominant_emotion
                return self._convert_numpy_types({
                    'emotion': dominant_emotion,
                    'confidence': confidence,
                    'all_emotions': emotion_scores
                })
            elif self.previous_emotion:
                # Fall back to previous emotion if new detection is low confidence
                return self._convert_numpy_types({
                    'emotion': self.previous_emotion,
                    'confidence': 0.0,
                    'all_emotions': emotion_scores,
                    'note': 'Low confidence, using previous emotion'
                })
            
            return None
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            return None 