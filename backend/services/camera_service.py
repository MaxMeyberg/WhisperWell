import logging
from deepface import DeepFace


logger = logging.getLogger('camera_service')


class CameraService:
    def __init__(self):
        #IMPORTANT TO READ EMOTIONS
        self.backends = ['opencv', 'ssd', 'dlib', 'mtcnn', 'fastmtcnn', 'retinaface', 'mediapipe', 'yolov8', 'yolov11s', 'yolov11n', 'yolov11m', 'yunet', 'centerface']
        #IMPORTANT FOR FACE RECOGNITION
        self.models= [ "VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace", "GhostFaceNet", "Buffalo_L" ]
    """ (click me for deets on )
    Deepface Functions:
    alignment_modes = [True, False]

    -----FACE VERIFICATION----- [WONT BE USED]
    result = DeepFace.verify(
        img1_path = "img1.jpg",
        img2_path = "img2.jpg",
        backend = "mtcnn"
    )

    -----FACE RECOGNITION IN DATABASE----- [WONT BE USED]
    dfs = DeepFace.find(
        img_path = "img1.jpg",
        db_path = "C:/workspace/my_db",
        backend = "mtcnn"
    )

    -----EMBEDDINGS----- [WONT BE USED]
    embeddings_objs = DeepFace.represent(
        img_path = "img.jpg",
        backend = "mtcnn"
    )

    #EXTRAS: actions = ['age', 'gender', 'race', 'emotion']
    -----ANALYZE EMOTION----- [WILL BE USED]
    objs = DeepFace.analyze(
        img_path = "img.jpg",
        actions = ['emotion'],
        backend = "mtcnn"
    )


    -----FACE DETECTION & ALIGNMENT----- [WONT BE USED]
    face_objs = DeepFace.extract_faces(
        img_path = "img.jpg", 
        detector_backend = "mtcnn",
        align = alignment_modes[0],
    )

    """

    
    def read_face(self, img):
        """Process image and return normalized emotion percentages"""
        try:
            img.save("logs/last_frame.jpg")
            # TODO: Add in the emotions
            objs = DeepFace.analyze(img_path = "logs/last_frame.jpg", actions = ['emotion'], detector_backend = "mtcnn", align = True)
            print("--------------------------------")

            emotions = objs[0]['emotion']
            print(self.format_percentages(emotions))
            return objs
        except Exception as e:
            logger.error(f"Error processing uploaded image: {e}")
            return None
    

    def format_percentages(self, emotions_data):
        """
        Format emotion data into normalized percentages
        
        Args:
            emotions_data (dict): Raw emotion scores
            
        Returns:
            dict: Formatted structure with normalized percentages
        """
        # Convert any numpy types to Python native types
        emotions = {k: float(v) for k, v in emotions_data.items()}
        
        # Calculate total for normalization
        total = sum(emotions.values())
        
        # Normalize to percentages
        normalized_emotions = {}
        for emotion, value in emotions.items():
            percentage = round((value / total) * 100, 1)  # Round to 1 decimal place
            normalized_emotions[emotion] = percentage
        
        # Sort emotions by percentage (highest first)
        sorted_emotions = dict(sorted(normalized_emotions.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True))
        
        # Get dominant emotion
        dominant_emotion = list(sorted_emotions.keys())[0]
        
        return {
            "dominant_emotion": dominant_emotion,
            "confidence": sorted_emotions[dominant_emotion],
            "emotions": sorted_emotions
        }
