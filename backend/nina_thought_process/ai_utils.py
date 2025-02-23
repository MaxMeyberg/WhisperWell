import logging

logger = logging.getLogger(__name__)

def get_ai_response(conversation, client=None):  
    try:
        if client is None:
            raise ValueError("OpenAI client not provided")
        
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",  # GPT-4 Turbo
            messages=conversation
        )
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"AI response error: {str(e)}")
        return f"Error: {str(e)}"