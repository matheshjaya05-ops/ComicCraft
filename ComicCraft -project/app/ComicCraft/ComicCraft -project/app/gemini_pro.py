from google import genai
from google.genai import types
from .config import GEMINI_API_KEY, GEMINI_STORY_MODEL, USE_MOCK_AI
from .schemas import ComicStory, ComicOutline

def _mock_story(outline, character, tone):
    return ComicStory(panels=[
        {
            "panel_number": p.panel_number,
            "caption": f"Meanwhile, the {tone} adventure continues...",
            "narration": p.scene_description,
            "dialogue": f"{character}: We have to keep going!"
        } for p in outline.panels
    ])

def generate_story(outline: ComicOutline, character: str, tone: str):
    if USE_MOCK_AI or not GEMINI_API_KEY:
        return _mock_story(outline, character, tone)

    client = genai.Client(api_key=GEMINI_API_KEY)
    schema = {
        "type": "object",
        "properties": {
            "panels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "panel_number": {"type": "integer"},
                        "caption": {"type": "string"},
                        "narration": {"type": "string"},
                        "dialogue": {"type": "string"}
                    },
                    "required": ["panel_number", "caption", "narration", "dialogue"]
                }
            }
        },
        "required": ["panels"]
    }
    outline_text = "\n".join(
        f"{p.panel_number}. {p.title}: {p.scene_description}"
        for p in outline.panels
    )
    prompt = f"""
Expand this comic outline into engaging panel-by-panel narration.
Main character: {character}
Tone: {tone}

Outline:
{outline_text}

Return one story object per panel. Keep panel_number unchanged.
Caption: short ambient/action caption.
Narration: 1-3 vivid sentences.
Dialogue: short character dialogue; do not overfill the panel.
Return only JSON matching the schema.
"""
    response = client.models.generate_content(
        model=GEMINI_STORY_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.9,
        ),
    )
    return ComicStory.model_validate_json(response.text)
