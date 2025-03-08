from openai import OpenAI
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from services.memory_service import MemoryClient #Mem0 [IN PROGRESS] This is a placeholder for the memory service
from dotenv import load_dotenv
import logging
import base64
from dev_loggers.logging_config import setup_loggers
import sys


# Import services
from services.chat_service import ChatService #Chat GPT
from services.image_service import ImageService #Black Forst Labs
from services.voice_service import VoiceService #Elevenlabs
from services.memory_service import MemoryService #Mem0 [IN PROGRESS]
from services.camera_service import CameraService #Face recognition

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)
#default character: Nina
character_id = 'Nina'
# Set up loggers
logger, camera_logger = setup_loggers()

#Flask is The messenger that lets the front end back end communicate w each other. PRAISE FLASK
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Initialize both clients
load_dotenv()
open_ai_client = OpenAI()  # It will automatically use OPENAI_API_KEY from environment
"""TODO: make a new folder called "Setup which calls all API keys"""
# Initialize services
chat_service = ChatService(
    api_key=os.getenv('OPENAI_API_KEY'),
)
image_service = ImageService(
    api_key=os.getenv('BLACK_FOREST_API_KEY'),
)
voice_service = VoiceService(
    api_key=os.getenv('ELEVENLABS_API_KEY')
)
camera_service = CameraService()

allChatHistory= {}
PREVIOUS_EMOTION = 'neutral'  # Track previous emotional state

"""
DONE: Manually write code for chat history
"""
#structure of the 
#decorator designed to create a URL path to OPEN AI 
@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "no data from memories"}), 400
            
        currMessage = data.get('message')
        sessionId = data.get('sessionId')  #TODO: USE THIS LATER WHEN MEM0 FULLY IMPLEMENTED
        voiceEnabled = data.get('voiceEnabled')
        character_id = data.get('character')
        user_face = data.get('userFace') # for face detection
        FLUX_model = data.get('model', 'standard')  # Add this line with default model

        # defaults to nina when a invalid character ID occurs
        if not character_id or character_id not in ["Nina", "Harold"]:
            logger.warning(f"Invalid character_id: {character_id}, defaulting to nina")
            character_id = "Nina"
        
        #Empty message case
        if not currMessage:
            """ (click) desc:
            HTTP Status Codes:
            200 = OK (Success)
            400 = Bad Request (Client Error)
            500 = Server Error

            Long code:
            --------------------------------[EXAMPLE]--------------------------------
            statusCode = 400
            #This will replace the "data" variable
            errorMessage = {"error": "No message provided"}
            #because JS is a bitch, we need to jsonify it
            errorMessage = jsonify(errorMessage)
            #This will be delivered to the front end where JS can read it correctly
            return errorMessage, statusCode
            
            """
            return jsonify({"error": "No message provided"}), 400
    
        # Use services for chat, emotion, and image generation
        ninaResponse, chatHistory, body_language_desc = chat_service.handle_chat(
            currMessage, sessionId, character_id, 
            user_face
        )
        #emotion is the variable which is a prompt describing the body language of the character
        image = image_service.generate_image(
            body_language_desc, 
            character_id=character_id,
            FLUX_model=FLUX_model
        )
        
        # Only generate voice if enabled
        audioData = None
        if voiceEnabled:
            audioData = voice_service.generate_speech(ninaResponse, character_id)
            if audioData:
                audioData = base64.b64encode(audioData).decode('utf-8')

        #Deliver all the info the front end
        return jsonify({
            "message": ninaResponse,
            "sessionId": sessionId,
            "therapistImage": image,
            "audioData": audioData
        })

    #catch the error into "e"
    except Exception as e:
        logger.warning(f"Chat endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/read_face_portal', methods=['POST'])
def detect_emotion_binary():
    try:
        # Get image file from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
            
        image_file = request.files['image']
        # Process with camera service
        result = camera_service.read_face(image_file)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='localhost', debug=True, port=5001)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        exit(1)
