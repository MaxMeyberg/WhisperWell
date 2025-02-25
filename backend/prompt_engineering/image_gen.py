"""
TODO: These are the prompts for the characters: 

Nina:
Grandpa:
Grandma:
"""

CHARACTERS = {
    "nina": {
        "base_appearance": """
        - Soft, youthful face with rosy cheeks and natural makeup
        - Medium-length dark brown bob with wispy side bangs
        - Large bright hazel eyes with long lashes
        - Small nose and gentle smile with pink lips
        - Black blazer over high-neck cream ribbed sweater
        - Professional office with bookshelves in background
        - Gold stud earrings
        - Warm, soft lighting from left side
        """,
        "image_path": "assets/Therapist-F-Smile.png",
        "style_requirements": """
        - Keep the exact art style with clean lines and soft shading
        - Maintain exact facial structure and proportions
        - Preserve the warm, inviting expression
        - Keep professional yet approachable demeanor
        - Maintain same lighting and composition
        """
    }
    # Add more characters here
}

def get_image_prompt(character_id, emotion):
    char = CHARACTERS[character_id]
    return f"""Match reference image exactly, changing only facial expression and subtle body language:
    
    Base Appearance (maintain exactly):
    {char["base_appearance"]}

    Current Emotional Expression: {emotion}
    
    Important:
    {char["style_requirements"]}
    - Change ONLY emotional expression while keeping core features
    """



