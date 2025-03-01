import logging
import cv2
import base64
import io
import numpy as np
from deepface import DeepFace
from PIL import Image
import json  # Add this for helper functions
import tensorflow as tf  # Add this import
import time

# Get the dedicated camera logger
logger = logging.getLogger('camera_service')

class CameraService:
    def __init__(self):
        self.previous_emotion = None
        self.confidence_threshold = 30  # Minimum confidence (30%) to report emotion
        
        # List of valid emotions to check against
        self.valid_emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
        # Test TensorFlow installation
        logger.info(f"TensorFlow version: {tf.__version__}")
        logger.info("GPU Available: {}".format(
            tf.config.list_physical_devices('GPU')
        ))
        
    def decode_base64_image(self, base64_string):
        """Convert base64 image to numpy array"""
        try:
            # Remove data URL prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
                
            # Decode base64
            image_bytes = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to a reasonable size for face detection
            image = image.resize((640, 480))
            
            # Debug the image at each step
            logger.info(f"PIL Image mode: {image.mode}, size: {image.size}")
            
            # Convert to numpy array and ensure correct color format
            image_array = np.array(image)
            # PIL gives us RGB, OpenCV expects BGR
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR).copy()
            
            return image_array
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
            image = self.decode_base64_image(image_data)
            
            # First try OpenCV face detection directly
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,  # More aggressive scaling
                minNeighbors=5,   # More reliable detections
                minSize=(30, 30)  # Minimum face size
            )
   
            
            # Draw rectangles on debug image
            debug_image = image.copy()
            for (x, y, w, h) in faces:
                cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green rectangle
                # Add text to show face detected
                cv2.putText(debug_image, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Add timestamp to the debug image
            timestamp = time.strftime("%H:%M:%S")
            cv2.putText(debug_image, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite('logs/last_frame.jpg', debug_image)  # Just update single file
            
            # Now try DeepFace
            try:
                result = DeepFace.analyze(
                    img_path=image, 
                    actions=['emotion'],
                    enforce_detection=False,
                    detector_backend='opencv',
                    align=True
                )
            except Exception as e:
                logger.error(f"DeepFace analysis failed: {e}")
                return None
            
            # Get emotion scores and log only the important parts
            emotion_scores = result[0]['emotion']
            
            # Get dominant emotion and score
            dominant_emotion = result[0]['dominant_emotion']
            
            # Validate emotion scores
            total_score = sum(emotion_scores.values())
            if total_score == 0:
                logger.error("Invalid emotion scores - all zeros")
                return None
            
            # Add sanity check for unreasonable scores
            if any(score > 1000 for score in emotion_scores.values()):
                logger.warning("Unreasonably high emotion scores detected, normalizing...")
                # Normalize all scores to be between 0 and 1
                max_score = max(emotion_scores.values())
                emotion_scores = {k: v/max_score for k, v in emotion_scores.items()}
            
            # Normalize scores to percentages
            normalized_scores = {
                emotion: (score / total_score) * 100 
                for emotion, score in emotion_scores.items()
            }
            
            # Find highest scoring emotion
            dominant_emotion = max(normalized_scores.items(), key=lambda x: x[1])[0]
            confidence = normalized_scores[dominant_emotion]
            
            logger.info(f"Face detected - Dominant emotion: {dominant_emotion}")
            logger.info("All emotion scores:")
            for emotion, score in emotion_scores.items():
                logger.info(f"  {emotion}: {score}")
            
            # Only return emotion if confidence is high enough
            if confidence >= self.confidence_threshold:
                self.previous_emotion = dominant_emotion
                logger.info(f"Using detected emotion: {dominant_emotion}")
                return self._convert_numpy_types({
                    'emotion': dominant_emotion,
                    'confidence': confidence,
                    'all_emotions': emotion_scores
                })
            elif self.previous_emotion:
                # Fall back to previous emotion if new detection is low confidence
                logger.info(f"Low confidence ({confidence}) - Using previous emotion: {self.previous_emotion}")
                return self._convert_numpy_types({
                    'emotion': self.previous_emotion,
                    'confidence': 0.0,
                    'all_emotions': emotion_scores,
                    'note': 'Low confidence, using previous emotion'
                })
            
            logger.info("No reliable emotion detected")
            return None
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            logger.exception("Full error details:")
            return None 