from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, GEMINI_OUTLINE_MODEL, PANELS, USE_MOCK_AI
from .schemas import ComicOutline

def _mock_outline(prompt, character, setting, tone, art_style, panels):
    return ComicOutline(panels=[
        {
            "panel_number": i,
            "title": f"Panel {i}",
            "scene_description": f"{character} continues the {tone} adventure in {setting}.",
            "image_prompt": f"{art_style} comic illustration of {character} in {setting}, panel {i}, cinematic composition, expressive characters, consistent character design"
        } for i in range(1, panels + 1)
    ])

def generate_outline(prompt, character, setting, tone, art_style, panels=None):
    panels = panels or PANELS
    if USE_MOCK_AI or not GEMINI_API_KEY:
        return _mock_outline(prompt, character, setting, tone, art_style, panels)

    client = genai.Client(api_key=GEMINI_API_KEY)
    schema = {
        "type": "object",
        "properties": {
            "panels": {
                "type": "array",
                "minItems": panels,
                "maxItems": panels,
                "items": {
                    "type": "object",
                    "properties": {
                        "panel_number": {"type": "integer"},
                        "title": {"type": "string"},
                        "scene_description": {"type": "string"},
                        "image_prompt": {"type": "string"}
                    },
                    "required": ["panel_number", "title", "scene_description", "image_prompt"]
                }
            }
        },
        "required": ["panels"]
    }
    instruction = f"""
Create exactly {panels} connected comic panels.
Story idea: {prompt}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return only JSON matching the supplied schema. Maintain visual continuity:
the same character appearance, clothing, colors and setting logic across panels.
Image prompts must describe the scene visually and must not contain written dialogue/text.
"""
    response = client.models.generate_content(
        model=GEMINI_OUTLINE_MODEL,
        contents=instruction,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.9,
        ),
    )
    return ComicOutline.model_validate_json(response.text)
