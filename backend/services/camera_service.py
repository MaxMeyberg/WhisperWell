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
        """Process image from file upload"""
        try:
            img.save("logs/last_frame.jpg")
            # TODO: Add in the emotions
            objs = DeepFace.analyze(img_path = "logs/last_frame.jpg", actions = ['emotion'], detector_backend = "mtcnn", align = True)
            print("--------------------------------")
            print(objs)
            return objs
        except Exception as e:
            logger.error(f"Error processing uploaded image: {e}")
            return None