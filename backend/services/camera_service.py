import logging
import cv2
import numpy as np
from deepface import DeepFace
import time

# Get the dedicated camera logger
logger = logging.getLogger('camera_service')

class CameraService:
    def __init__(self):
        self.previous_emotion = None
        self.confidence_threshold = 30  # Minimum confidence (30%) to report emotion
        self.detector_backend = 'opencv'  # Default detector
        self.available_backends = ['opencv', 'mtcnn', 'retinaface']
        
        logger.info(f"Using face detector: {self.detector_backend}")
        
    def process_image(self, img_np):
        """Process image directly with no encoding/decoding"""
        try:
            # Resize to standard size if needed
            if img_np.shape[0] > 480 or img_np.shape[1] > 640:
                img_np = cv2.resize(img_np, (640, 480))
            
            # Detect faces
            faces = self._locate_faces(img_np)
            
            # Analyze emotions
            emotion_data = self._analyze_emotions(img_np)
            if emotion_data is None:
                return None
            
            dominant_emotion, confidence, emotion_scores = emotion_data
            
            # Create debug image
            self.green_box(img_np.copy(), faces, dominant_emotion, confidence)
            
            # Return the emotion data
            return self._format_emotion_response(dominant_emotion, confidence, emotion_scores)
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
            
    def detect_face_from_file(self, image_file):
        """Process image from file upload"""
        try:
            # Read image file into numpy array
            img_bytes = image_file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Process using our simplified method
            return self.process_image(img_np)
            
        except Exception as e:
            logger.error(f"Error processing uploaded image: {e}")
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

    def green_box(self, img, faces, dom_emo=None, confidence=None):
        """Draw debug information on the image"""
        # Add timestamp
        cv2.putText(img, time.strftime("%A:%D   Time(24H):%H:%M"), (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # For each face, draw green rectangle
        for x, y, w, h in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if dom_emo and confidence:
                label = f"{dom_emo} ({confidence:.1f}%)"
                cv2.putText(img, label, (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save the result
        cv2.imwrite('logs/last_frame.jpg', img)

    def _analyze_emotions(self, image):
        """Analyze emotions using DeepFace"""
        try:
            result = DeepFace.analyze(
                img_path=image, 
                actions=['emotion'],
                enforce_detection=False,
                detector_backend=self.detector_backend,
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
            
            logger.info(f"Face detected - Dominant emotion: {dominant_emotion}")
            
            return dominant_emotion, confidence, emotion_scores
            
        except Exception as e:
            logger.error(f"DeepFace analysis failed: {e}")
            return None

    def _normalize_emotion_scores(self, emotion_scores):
        """Normalize emotion scores to percentages"""
        total_score = sum(emotion_scores.values())
        if total_score == 0:
            return None
        
        # Convert to percentages
        return {
            emotion: (score / total_score) * 100 
            for emotion, score in emotion_scores.items()
        }

    def _format_emotion_response(self, dominant_emotion, confidence, emotion_scores):
        """Prepare the response based on confidence threshold"""
        # Convert numpy types to standard Python types
        emotion_scores = {k: float(v) for k, v in emotion_scores.items()}
        
        # High confidence case
        if confidence >= self.confidence_threshold:
            self.previous_emotion = dominant_emotion
            return {
                'emotion': dominant_emotion,
                'confidence': float(confidence),
                'all_emotions': emotion_scores
            }
        
        # Fall back to previous emotion if available
        elif self.previous_emotion:
            return {
                'emotion': self.previous_emotion,
                'confidence': 0.0,
                'all_emotions': emotion_scores,
                'note': 'Low confidence, using previous emotion'
            }
        
        # No reliable emotion detected
        return None
    
    def set_detector(self, backend_name):
        """Change the face detector backend"""
        if backend_name in self.available_backends:
            self.detector_backend = backend_name
            logger.info(f"Changed face detector to: {backend_name}")
            return True
        else:
            logger.warning(f"Invalid backend: {backend_name}")
            return False 

    def save_current_image(self, image, filename='logs/last_frame.jpg'):
        """Save the current image to disk"""
        try:
            # Save to file
            cv2.imwrite(filename, image)
            
            return True
        except Exception as e:
            logger.error(f"Error saving image: {e}")
            return False 