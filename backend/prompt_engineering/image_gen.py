"""

Nina:
Grandpa:
Grandma:
"""

CHARACTERS = {
    "nina": {
        "base_prompt": "Young Asian-European woman therapist with dark brown bob cut, hazel eyes, and black blazer",
        "base_appearance": """
        # Core Features (MUST remain exactly the same):
        - Exact same face shape and bone structure
        - Identical Asian-European facial features
        - Same dark brown bob haircut with center part
        - Identical eye shape and size (large almond eyes)
        - Same nose shape and size (small, defined bridge)
        - Exact same lip shape and fullness
        - Identical facial proportions and placement
        - Same gold hoop earrings
        - Identical black blazer and cream turtleneck

        # Style Elements (Must match exactly):
        - High-end commercial anime/webtoon style
        - Ultra-clean linework with same line weights
        - Identical skin texture and highlight placement
        - Same hair rendering with grouped strands
        - Exact same makeup style and application
        - Identical lighting setup and shadows
        - Same background with bookshelves
        - Matching color palette and grading

        # Only These Can Change:
        - Facial expression and micro-expressions
        - Eye contact and gaze direction
        - Slight head tilt or position
        - Subtle changes in eyebrow position
        - Minor variations in smile/lip position
        - Small shifts in body language
        """,
        "image_path": "assets/Nina.png",
        "style_requirements": """
        - Maintain exact clean anime/webtoon style
        - Crisp lines with subtle shading
        - Subtle gradients in hair and clothing
        - Soft highlight on eyes to maintain engagement
        - Slightly stylized proportions consistent with reference
        - Professional office background with bookshelves
        """
    },
    "Harold": {
        "base_prompt": "Elderly 72-year-old man with white hair, glasses, and distinguished facial features",
        "base_appearance": """
        # Core Features (MUST remain exactly the same):
        - Elderly man (72 years old) with dignified appearance
        - Caucasian with weathered but healthy complexion
        - White hair neatly trimmed, with swept-back style
        - Rectangular silver-rimmed glasses
        - Distinguished facial features with kind wrinkles
        - Bright blue eyes with crow's feet
        - Straight nose with slightly wider bridge
        - Maintained gray-white mustache and trimmed beard
        - Navy blue blazer with light blue dress shirt
        - Gold pocket watch chain visible

        # Style Elements (Must match exactly):
        - High-end commercial anime/webtoon style
        - Clean linework with emphasis on facial details
        - Subtle highlight on glasses and hair
        - Professional office background with bookshelves
        - Warm, professional lighting
        - Slightly deeper shadows to emphasize age
        - Same rendering style as Nina character
        - Matching color palette with slightly warmer tones

        # Only These Can Change:
        - Facial expression and micro-expressions
        - Eye contact and gaze direction
        - Slight head tilt or position
        - Hand gestures (occasionally visible)
        - Eyebrow position to indicate thought or concern
        - Mouth position for different speaking expressions
        """,
        "image_path": "assets/Harold.png",
        "style_requirements": """
        - Maintain exact clean anime/webtoon style
        - Detailed facial features showing age appropriately
        - Slightly deeper lines and more textured than Nina
        - Same lighting style and highlight placement
        - Consistent professional background with dark wood tones
        - Maintain glasses and facial hair styling exactly
        """
    }
}

def get_image_prompt(character_id, body_language):
    char = CHARACTERS.get(character_id, {})
    base_prompt = char.get("base_prompt", "Person with neutral expression")
    style_req = char.get("style_requirements", "Maintain consistent art style")
    
    expression = body_language.get('expression', 'neutral')
    gesture = body_language.get('gesture', 'standard pose')
    
    prompt = f"""
    {base_prompt} with {expression}. {gesture}.
    
    Maintain exact art style consistency:
    {style_req}
    - Only change emotional expression
    - Keep all core features identical to reference image
    - DO NOT CHANGE THE WAY THE IMAGE LOOKS, ONLY
    """
    
    return prompt



