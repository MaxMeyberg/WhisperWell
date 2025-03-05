"""PIPELINE (click for deets)
Image capture → Processing → Face detection → Emotion analysis
"""
import logging #needed for logging into backend terminal
import cv2 # this is the openCV library, like tf2, the cv2 is the good one
import base64 #base 64 data is important because it converts text -> binary AND binary -> text
import io #this is needed to convert image to binary (includes io.BytesIO) Also uses RAM
import numpy as np # converts images to numpy arrays (They are Arrays in C that are faster)
from deepface import DeepFace #Works on emotion detection (Can do other stuff like face recognition)
from PIL import Image #Makes it so that the binary from images is digestible for numpy to convert into numpy arrays
import json # Needed for JSON files (aka how to send to frontend)
import tensorflow as tf # needed for deepface to actually work, Deepface isnt an API, its a library
import time #needed for timing

logger = logging.getLogger('camera_service') #needed for backend terminal logging for camera, shows stuff like emotion spotted on terminal

class CameraService:
    def __init__(self):
        self.previous_emotion = None # We need previous emotions to have more context for now nina should react
        self.confidence_threshold = 30 # need at least 30% for an emotion to show reaction
        self.valid_emotions = ['happy', 'sad', 'angry', 'disgusted', 'surprised', 'fearful', 'neutral'] # Deep think is powere by these 7 emotions

        # Tensorflow version + GPU Check needed to see if deepface can work
        logger.info(f"Tensorflow version: {tf.__version__}") 
        logger.info("GPU Available: {}".format(
            tf.config.list_physical_devices('GPU')
        ))
    """Converts base64 string to numpy array"""
    def decode_base64_to_npArray(self, base_64str):
        try:
            """
            BEFORE:
            "data:image/jpeg;base64,Deez Nutz"

            AFTER:
            "Deez Nutz"

            Designed in a way to handle more than images from webcams
            Other stuff we can do w the bigger code written
            EX: Image uploading, external APIs, etc
            """

            if base_64str.startswith('data:'):
                if ';base64,' in base_64str:
                    # common URL Format
                    base_64str = base_64str.split(',')[1]
                else:
                    # other data URL format
                    base_64str = base_64str.split(',',1)[1]
            #remove whitespace, decoding will crash if we don use whitespace
            base_64str = base_64str.strip()

            # decode base64 to binary
            img_binary = base64.b64decode(base_64str)

            """convert binary to PIL Image(click for deets)
            img_binary: b\xff\xd8\xff\xe0\x00\x10JFIF...
            ioBytesIO: allows us to convert binary to PIL Image (image is now readable for numpy)
            PIL_img: put image into a variable
            """
            PIL_img = Image.open(io.BytesIO(img_binary))

            #put all images in RGB format:
            if PIL_img.mode != 'RGB':
                PIL_img = PIL_img.convert('RGB')
            #get small image size, so we dont blow up the RAM
            PIL_img = PIL_img.resize((640, 480))

            #convert to numpy array
            img_arr = np.array(PIL_img)

            # 
            """(click for deets)
            create a numpy array of the 3 RGB channels [R,G,B], each value is a 2D array of reg, green and blue

            PIL uses RGB (Red-Green-Blue) order
            OpenCV uses BGR (Blue-Green-Red) order
            """
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_RGB2BGR)

            return img_arr
        except Exception as e:
            logger.error(f"Error decoding base64 to numpy array: {e}")
            return None

    """converts the numpyTypes into python types"""
    def convert_numpy_types(self, obj):
        # Integer
        if isinstance(obj, np.integer): return int(obj)
        # Float
        if isinstance(obj, np.floating): return float(obj)
        # List
        if isinstance(obj, list): return [self.convert_numpy_types(item) for item in obj]
        # Dict
        if isinstance(obj, dict): return {k: self.convert_numpy_types(v) for k, v in obj.items()}
        #NP array
        if isinstance(obj, np.ndarray): return obj.tolist()
        # everything else
        return obj
    
    """
    This function detects the face to check for emotions and returns the emotion chart (dom_emo, conf, and emo_Score)
    """
    def detect_face(self, base64_img):
        try:
            # Step 1: decode to numpy array
            img_npArr = self.decode_base64_to_npArray(base64_img)
            if img_npArr is None: return None

            # Step 2: Analyze emotions w DeepFace (Shows the emotion scores, confidence and dom_emo)
            emotions = self.analyze_emotions(img_npArr)
            if emotions == None: return None

            # Step 3: detect faces
            faces = self.locate_faces(img_npArr)

            """(click for deets) on rough example
            dom_emo: "happy" 
            confidence: 0.83
            emo_scores:{
                "happy": 0.83,
                "sad": 0.12,
                "angry": 0.05,
                "disgusted": 0.00,
                "surprised": 0.00,
                "fearful": 0.00,
                "neutral": 0.00
            }
            """
            dom_emo, conf, emo_scores = emotions
            # Step 4: [DEVELOPER TOOL] Create the green recangle image, use copy to make future features easier to add
            self.green_box(img_npArr.copy(), faces, dom_emo, conf)

            # Step 5: return confidence table
            return self.prepare_emotion_response(emotions)

        except Exception as e:
            logger.error(f"Error in emotion detection: {e}")
            return None

    def green_box(self, img, faces, dom_emo=None, confidence=None):
        """(click for deets) Why we make a copy
        We wanna create a copy so we can scribble thie one with 
        funny green boxes. And if we have the original one, 
        it would make adding more features easier
        """
        
        # Add timestamp
        cv2.putText(img, time.strftime("%A:%D   Time(24H):%H:%M"), (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # For each face, draw green rectangle
        for x, y, w, h in faces:
            # Draw rectangle
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Add emotion label if available
            if dom_emo and confidence:
                # the .0 in this is to say by the 0th decimal
                label = f"{dom_emo} ({confidence:.1f}%)"
                cv2.putText(img, label, (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Save the result
        cv2.imwrite('logs/last_frame.jpg', img)

    """(click for deets)
    TODO: Add mtcnn to be the new default 
    cv2.CascadeClassifier()

    This is an algorithm that uses patterns of light and dark regions to identify faces
    Much faster than deep learning models, but less accurate in challenging conditions"

    cv2.data.haarcascades  # Path to built-in OpenCV models
    + 'haarcascade_frontalface_default.xml'  # Specific face detection model

    TLDR: Creates a detector that can find faces in an image, This is a pre-trained Model made in OpenCV, dont worry for now on complex ML stuff
    """
    def locate_faces(self, image):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        #quickly convert to grayscale so face detection is 3x faster,
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

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

    def _format_emotion_response(self, dominant_emotion, confidence, emotion_scores):
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