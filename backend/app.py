from openai import OpenAI
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from mem0 import MemoryClient
from dotenv import load_dotenv
from nina_thought_process import ( get_ai_response, analyze_emotional_context, nina_personality)  # This works because of __init__.py, w.o init.oy we would need to imoort each of these 1 by 1.   
import logging
from image_generation import generate_image
from voice_generation import generate_speech
from accounts import get_login, get_memories, add_memory
import base64

# I love Lobotomy Corp, and I wanted to make the custom logger for fun
class CustomLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def zayin(self, message):      # Instead of debug
        self.logger.debug(message)
    
    def teth(self, message):       # Instead of info
        self.logger.info(message)
    
    def he(self, message):       # Instead of warning
        self.logger.warning(message)
    
    def waw(self, message):       # Instead of error
        self.logger.error(message)
    
    def aleph(self, message):        # Instead of critical
        self.logger.critical(message)

# Create our custom logger


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
log = CustomLogger(logger)

#Flask is The messenger that lets the front end back end communicate w each other. PRAISE FLASK
app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Initialize both clients
load_dotenv()
open_ai_client = OpenAI()  # It will automatically use OPENAI_API_KEY from environment
mem0_client = MemoryClient(api_key=os.environ['MEM0_API_KEY'])


allChatHistory= {}
PREVIOUS_EMOTION = 'neutral'  # Track previous emotional state

def summarize_conversation(conversation):
    """Get a summary of the current conversation"""
    summary_prompt = [
        {"role": "system", "content": "Summarize the key points of this conversation, focusing on important information about the user."},
        *conversation
    ]
    
    summary = get_ai_response(summary_prompt, client=open_ai_client)
    return summary

def get_running_summary(conversation):
    """Get a concise running summary of the conversation"""
    summary_prompt = [
        {"role": "system", "content": """
            Maintain a very concise running summary of the key points about the user. 
            Focus on facts, preferences, and important context.
            Format as bullet points.
            Keep only the most relevant information.
            Limit to 3-5 bullet points.
        """},
        *conversation
    ]
    
    summary = get_ai_response(summary_prompt, client=open_ai_client)
    return summary


"""
DONE: Manually write code for chat history
"""
#structure of the 
#decorator designed to create a URL path to OPEN AI 
@app.route('/api/chat', methods=['POST'])
def chat():
    #try is needed cause if the user sends a bad request, it will return an error
    try: 
        #"data" is from the App.js file, copy paste this text to see location:
        data = request.json
        """
        body: JSON.stringify({
        message: text,
        sessionId: 'default',
        voiceEnabled: voiceEnabled,
        model: selectedModel
        })
        """
        currMessage =  data.get('message')
        sessionId = data.get('sessionId') #TODO: USE THIS LATER WHEN MEM0 FULLY IMPLEMENTED
        voiceEnabled = data.get('voiceEnabled')
        currModel = data.get('model') #default is gpt-3.5
        
        #Empty message case
        if not currMessage:
            """
            HTTP Status Codes:
            200 = OK (Success)
            400 = Bad Request (Client Error)
            500 = Server Error
            """
            statusCode = 400
            #This will replace the "data" variable
            errorMessage = {"error": "No message provided"}
            #because JS is a bitch, we need to jsonify it
            errorMessage = jsonify(errorMessage)
            #This will be delivered to the front end where JS can read it correctly
            return errorMessage, statusCode

        #print in ternimal backend to see what the user likes, EX: voice, model, input text. The 3 lines mean same thing
        logger.debug(f"Using {currModel}")
        logger.debug(f"Voice Mode: {voiceEnabled}")
        logger.debug(f"Nina heard you say: {currMessage}")

        #A new session w Nina, runs this
        if sessionId not in allChatHistory:
            #get Nina's personality from the prompt.py
            systemPrompt = nina_personality()
            """ (click for more deets)
            --------------------------------[CONCEPT]--------------------------------
            We need to follow OPEN AI's API format, for GPT to read it

            # 1. "system" - Instructions or context for the AI
            {
                "role": "system",
                "content": "You are Nina, a 21-year-old therapist..."
            }

            # 2. "user" - What the human says
            {
                "role": "user", 
                "content": "I feel sad today"
            }

            # 3. "assistant" - What Nina (AI) says
            {
                "role": "assistant",
                "content": "I understand how you're feeling..."
            }
            --------------------------------[EXAMPLE]--------------------------------

            Pattern in allChatHistory[sessionId]:
            [
                {"role": "system", "content": nina_personality()},
                {"role": "user", "content": "I feel sad today"},
                {"role": "assistant", "content": "I hear you..."},
                {"role": "user", "content": "my parrot died"},
                {"role": "assistant", "content": "Awww, it hurts to lose a pet. I recently lost my hamster..."},
            ]

            """
            allChatHistory[sessionId] = [{"role": "system", "content": systemPrompt}]
        
        #Register chat History 
        allChatHistory[sessionId].append({"role": "user", "content": currMessage})
        #register the chat history for this current talk with Nina
        chatHistory = allChatHistory[sessionId]
        #send chatHistory to OPEN AI w get_ai_response, also takes care of what type of model to use
        ninaResponse = get_ai_response(chatHistory, client=open_ai_client)
        #add nina's response to the chat history
        chatHistory.append({"role": "assistant", "content": ninaResponse})
        log.zayin("Nina says: " + ninaResponse)

        emotion = analyze_emotional_context(chatHistory, client=open_ai_client)
        image = generate_image(emotion)
        #see if voice is enabled to turn on/off audio
        audioData = generate_speech(ninaResponse) if voiceEnabled else None
        #audioData is actually in Binary now, so to make it into actual text: we do this voodo stuff:
        audioData = base64.b64encode(audioData).decode('utf-8') if audioData != None else None

        #Deliver all the info the front end
        return jsonify({
            "message": ninaResponse,
            "sessionId": sessionId,
            "therapistImage": image,
            "audioData": audioData
        })

    #catch the error into "e"
    except Exception as e:
        log.he(f"Chat endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500




@app.route('/api/speech', methods=['POST'])
def generate_speech_endpoint():
    try:
        data = request.json
        if not data:
            logger.error("No data provided in speech request")
            return jsonify({"error": "No data provided"}), 400
            
        text = data.get('text')
        if not text:
            logger.error("No text provided in speech request")
            return jsonify({"error": "No text provided"}), 400
            
        logger.info(f"Generating speech for text: {text[:50]}...")
        audio_data = generate_speech(text)
        
        if not audio_data:
            logger.error("Failed to generate speech")
            return jsonify({"error": "Speech generation failed"}), 500
            
        # Convert audio data to base64 for frontend
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({
            "audio": audio_base64,
            "format": "audio/mpeg"
        })
        
    except Exception as e:
        logger.error(f"Speech endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_memory', methods=['GET'])
def test_memory():
    try:
        # Create test conversation
        test_conversation = [
            {"role": "user", "content": "Hi Nina, I'm vegetarian and I love cooking."},
            {"role": "assistant", "content": "That's great! I'll remember that you're vegetarian. What kind of dishes do you like to cook?"}
        ]
        
        # Add to memory
        add_memory("test_user", test_conversation)
        
        # Test retrieving memory with different queries
        veg_memories = get_memories("test_user", query="vegetarian")
        cooking_memories = get_memories("test_user", query="cooking")
        
        return jsonify({
            "status": "success",
            "vegetarian_related": veg_memories,
            "cooking_related": cooking_memories,
            "all_memories": get_memories("test_user")
        })
        
    except Exception as e:
        logger.error(f"Memory test error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/end_session', methods=['POST'])
def end_session():
    """Save session summary to long-term memory"""
    try:
        data = request.json
        sessionId = data.get('sessionId', 'default')
        
        if sessionId in allChatHistory:
            # Get final summary of the session
            session_summary = summarize_conversation(allChatHistory[sessionId])
            
            # Save to long-term memory
            add_memory(sessionId, [{
                "role": "system",
                "content": f"Session Summary: {session_summary}"
            }])
            
            # Clear the session
            del allChatHistory[sessionId]
            
            return jsonify({"status": "success", "summary": session_summary})
            
    except Exception as e:
        logger.error(f"End session error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(host='localhost', debug=True, port=5001)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        exit(1)
