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
        
    def decode_base64_to_npArray(self, base64_string):
        """Convert base64 image to numpy array"""
        try:
            # Step 1: Extract base64 data
            clean_base64 = self._extract_base64_data(base64_string)
            
            # Step 2: Create image from binary data
            image = self._create_image_from_base64(clean_base64)
            if image is None:
                return None
            
            # Step 3: Process and convert to numpy array
            return self._convert_image_to_array(image)
            
        except Exception as e:
            logger.error(f"Error decoding image: {e}")
            return None
        
    def _extract_base64_data(self, base64_string):
        """Extract the actual base64 data from various possible formats"""
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        return base64_string

    def _create_image_from_base64(self, base64_string):
        """Create a PIL image from base64 string"""
        try:
            # Decode base64 to binary
            image_bytes = base64.b64decode(base64_string)
            
            # Create PIL Image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to a reasonable size for face detection
            image = image.resize((640, 480))
            
            # Log image details
            logger.info(f"PIL Image mode: {image.mode}, size: {image.size}")
            
            return image
        except Exception as e:
            logger.error(f"Failed to create image from base64: {e}")
            return None

    def _convert_image_to_array(self, image):
        """Convert PIL image to OpenCV-compatible numpy array"""
        # Convert to numpy array
        image_array = np.array(image)
        
        # PIL gives us RGB, OpenCV expects BGR
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR).copy()
        
        return image_array
    
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
            # Step 1: Decode and detect faces
            image = self.decode_base64_to_npArray(image_data)
            if image is None:
                return None
            
            faces = self._locate_faces(image)
            
            # Step 2: Create debug image
            self._create_debug_image(image, faces)
            
            # Step 3: Analyze emotions with DeepFace
            emotion_data = self._analyze_emotions(image)
            if emotion_data is None:
                return None
            
            dominant_emotion, confidence, emotion_scores = emotion_data
            
            # Step 4: Return results based on confidence
            return self._prepare_emotion_response(dominant_emotion, confidence, emotion_scores)
            
        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            logger.exception("Full error details:")
            return None

    def _locate_faces(self, image):
        """Locate faces in image using OpenCV"""
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=5,
            minSize=(30, 30)
        )

    def _create_debug_image(self, image, faces):
        """Save debug image with faces marked and timestamp"""
        # Create copy and add timestamp
        debug_img = image.copy()
        cv2.putText(debug_img, time.strftime("%H:%M:%S"), (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw rectangles for all detected faces
        for face in faces:
            x, y, w, h = face
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(debug_img, 'Face', (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save image
        cv2.imwrite('logs/last_frame.jpg', debug_img)

    def _analyze_emotions(self, image):
        """Analyze emotions using DeepFace"""
        try:
            result = DeepFace.analyze(
                img_path=image, 
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv',
                align=True
            )
            
            # Process emotion scores
            emotion_scores = result[0]['emotion']
            
            # Normalize scores
            normalized_scores = self._normalize_emotion_scores(emotion_scores)
            if normalized_scores is None:
                return None
            
            # Find dominant emotion
            dominant_emotion = max(normalized_scores.items(), key=lambda x: x[1])[0]
            confidence = normalized_scores[dominant_emotion]
            
            # Log results
            logger.info(f"Face detected - Dominant emotion: {dominant_emotion}")
            logger.info("All emotion scores:")
            for emotion, score in emotion_scores.items():
                logger.info(f"  {emotion}: {score}")
            
            return dominant_emotion, confidence, emotion_scores
            
        except Exception as e:
            logger.error(f"DeepFace analysis failed: {e}")
            return None

    def _normalize_emotion_scores(self, emotion_scores):
        """Normalize emotion scores to percentages"""
        # Validate scores
        total_score = sum(emotion_scores.values())
        if total_score == 0:
            logger.error("Invalid emotion scores - all zeros")
            return None
        
        # Handle unreasonably high scores
        if any(score > 1000 for score in emotion_scores.values()):
            logger.warning("Unreasonably high emotion scores detected, normalizing...")
            max_score = max(emotion_scores.values())
            emotion_scores = {k: v/max_score for k, v in emotion_scores.items()}
            total_score = sum(emotion_scores.values())
        
        # Convert to percentages
        return {
            emotion: (score / total_score) * 100 
            for emotion, score in emotion_scores.items()
        }

    def _prepare_emotion_response(self, dominant_emotion, confidence, emotion_scores):
        """Prepare the response based on confidence threshold"""
        # High confidence case
        if confidence >= self.confidence_threshold:
            self.previous_emotion = dominant_emotion
            logger.info(f"Using detected emotion: {dominant_emotion}")
            return self._convert_numpy_types({
                'emotion': dominant_emotion,
                'confidence': confidence,
                'all_emotions': emotion_scores
            })
        
        # Fall back to previous emotion if available
        elif self.previous_emotion:
            logger.info(f"Low confidence ({confidence}) - Using previous emotion: {self.previous_emotion}")
            return self._convert_numpy_types({
                'emotion': self.previous_emotion,
                'confidence': 0.0,
                'all_emotions': emotion_scores,
                'note': 'Low confidence, using previous emotion'
            })
        
        # No reliable emotion detected
        logger.info("No reliable emotion detected")
        return None 