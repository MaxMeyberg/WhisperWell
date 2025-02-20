from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
from openai import OpenAI
from mem0 import MemoryClient
from dotenv import load_dotenv
from prompts import cbtprompt_v0, robust_v0
import logging
import requests
from image_generation import generate_therapist_image
from voice_generation import generate_speech
from accounts import get_login, get_memories, add_memory
import base64



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
mem0_client = MemoryClient(api_key=os.environ['MEM0_API_KEY'])


conversations = {}
PREVIOUS_EMOTION = 'neutral'  # Track previous emotional state

def get_ai_response(conversation, model="gpt-3.5"):
    try:
        if model == "gpt-4":
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=conversation
            )
            return response.choices[0].message.content
        elif model == "gpt-3.5":
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=conversation
            )
            return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI response error for model {model}: {str(e)}")
        return f"Error with {model}: {str(e)}"

def summarize_conversation(conversation):
    """Get a summary of the current conversation"""
    summary_prompt = [
        {"role": "system", "content": "Summarize the key points of this conversation, focusing on important information about the user."},
        *conversation
    ]
    
    summary = get_ai_response(summary_prompt)
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
    
    summary = get_ai_response(summary_prompt)
    return summary

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        session_id = data.get('sessionId', 'default')
        user_message = data.get('message')
        voice_enabled = data.get('voiceEnabled', False)
        model = data.get('model', 'gpt-3.5')
        
        logger.info(f"Received request - Model: {model}, Voice: {voice_enabled}")  # This will help debug
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Initialize conversation if needed
        if session_id not in conversations:
            system_prompt = cbtprompt_v0() + robust_v0()
            conversations[session_id] = [{"role": "system", "content": system_prompt}]
        
        # Get AI response
        bot_reply = get_ai_response(conversations[session_id], model)
        if not bot_reply:
            return jsonify({"error": "Failed to get AI response"}), 500
        
        # Get emotional context and generate image
        emotion = analyze_emotional_context(conversations[session_id])
        new_image_url = generate_therapist_image(emotion)
        
        # Generate audio only if voice is enabled
        audio_data = None
        if voice_enabled:
            audio_data = generate_speech(bot_reply)
        
        # Nina will keep track of what you say and what she says
        conversations[session_id].append({"role": "user", "content": user_message})
        conversations[session_id].append({"role": "assistant", "content": bot_reply})
        
        # Update running summary after each exchange
        current_summary = get_running_summary(conversations[session_id])
        
        # Replace old summary if it exists, or add new one
        summary_index = next((i for i, msg in enumerate(conversations[session_id]) 
                            if msg["role"] == "system" and "Current Summary:" in msg["content"]), None)
        
        if summary_index is not None:
            conversations[session_id][summary_index] = {
                "role": "system",
                "content": f"Current Summary: {current_summary}"
            }
        else:
            conversations[session_id].append({
                "role": "system",
                "content": f"Current Summary: {current_summary}"
            })
        
        # Save summary to long-term memory instead of raw conversation
        add_memory(session_id, [{
            "role": "system",
            "content": f"Conversation Summary: {current_summary}"
        }])
        
        # Get relevant past summaries for context
        memories = get_memories(session_id, query=user_message)
        if memories:
            conversations[session_id].extend([
                {"role": "system", "content": "Previous relevant memories:"},
                *memories
            ])
        
        return jsonify({
            "message": bot_reply,
            "sessionId": session_id,
            "therapistImage": new_image_url,
            "audioData": base64.b64encode(audio_data).decode('utf-8') if audio_data else None
        })
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_emotional_context(conversation) -> str:
    """Analyze conversation with deeper contextual understanding"""
    recent_messages = conversation[-15:]
    current_emotion = 'neutral'
    
    # Core emotional indicators
    emotional_patterns = {
        'trauma': {
            'direct': ['trauma', 'abuse', 'assault', 'death', 'suicide'],
            'phrases': [
                'voices in my head', 'shadows', 'demons', 'haunting me',
                'cant escape', 'make it stop', 'hurting myself'
            ],
            'context': [
                'little', 'dark', 'scary', 'demean', 'control', 'trapped',
                'flashback', 'nightmare', 'memory'
            ]
        },
        'anxiety': {
            'direct': ['anxiety', 'panic', 'stress', 'worried'],
            'phrases': [
                'cant stop thinking', 'what if', 'something bad',
                'heart racing', 'overthinking', 'cant breathe'
            ],
            'context': [
                'maybe', 'probably', 'might be', 'feeling like',
                'nervous', 'shaking', 'tight chest'
            ]
        },
        'depression': {
            'direct': ['depression', 'depressed', 'hopeless'],
            'phrases': [
                'whats the point', 'no one cares', 'better off without',
                'cant feel anything', 'empty inside', 'tired of everything'
            ],
            'context': [
                'anymore', 'always', 'never', 'worthless', 'burden',
                'exhausted', 'numb'
            ]
        }
    }

    positive_streak = 0
    serious_topic_mentioned = False
    
    def check_pattern_match(content: str, patterns: dict) -> bool:
        # Check direct words
        if any(word in content for word in patterns['direct']):
            return True
        
        # Check phrases
        if any(phrase in content for phrase in patterns['phrases']):
            return True
            
        # Check contextual indicators
        context_matches = sum(1 for word in patterns['context'] if word in content)
        return context_matches >= 2  # Require multiple context matches
    
    for message in reversed(recent_messages):
        if message.get('role') == 'user':
            content = message.get('content', '').lower()
            
            # Check for complex emotional patterns
            for category, patterns in emotional_patterns.items():
                if check_pattern_match(content, patterns):
                    serious_topic_mentioned = True
                    if category == 'trauma':
                        return 'concerned_serious'
                    return 'concerned'
            
            # Look for subtle distress indicators
            distress_indicators = [
                ('i dont know', 'confused'),
                ('like', 'little', 'shadows'),  # Metaphorical description
                ('feeling', 'think', 'maybe'),  # Uncertainty markers
                ('always', 'never', 'everything'),  # Absolutist language
                ('cant', 'wont', 'shouldnt')  # Negative self-talk
            ]
            
            # Count matching indicator patterns
            indicator_matches = sum(
                1 for indicators in distress_indicators 
                if sum(1 for word in indicators if word in content) >= 2
            )
            
            if indicator_matches >= 2:
                return 'concerned'
            
            # Rest of the emotion checking logic...
            if any(word in content for word in ['sad', 'unhappy', 'lonely']):
                return 'sad'
            elif any(word in content for word in ['angry', 'mad', 'furious']):
                return 'angry'
            elif any(word in content for word in ['worried', 'anxious', 'nervous']):
                return 'anxious'
            
    return 'neutral' if not serious_topic_mentioned else 'concerned'




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
        session_id = data.get('sessionId', 'default')
        
        if session_id in conversations:
            # Get final summary of the session
            session_summary = summarize_conversation(conversations[session_id])
            
            # Save to long-term memory
            add_memory(session_id, [{
                "role": "system",
                "content": f"Session Summary: {session_summary}"
            }])
            
            # Clear the session
            del conversations[session_id]
            
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
