from google import genai
from google.genai import types

from .config import (
    GEMINI_API_KEY,
    GEMINI_OUTLINE_MODEL,
    PANELS,
    USE_MOCK_AI
)

from .schemas import ComicOutline


def create_mock_outline(
    prompt,
    character,
    setting,
    tone,
    art_style,
    panels
):
    result = []

    for i in range(1, panels + 1):
        result.append({
            "panel_number": i,
            "title": f"Panel {i}",
            "scene_description":
                f"{character} continues the {tone} adventure "
                f"in {setting}.",
            "image_prompt":
                f"{art_style} comic illustration of "
                f"{character} in {setting}, "
                f"panel {i}, cinematic composition, "
                f"expressive character, consistent character design."
        })

    return ComicOutline(panels=result)


def generate_outline(
    prompt,
    character,
    setting,
    tone,
    art_style,
    panels=None
):
    panels = panels or PANELS

    if USE_MOCK_AI or not GEMINI_API_KEY:
        return create_mock_outline(
            prompt,
            character,
            setting,
            tone,
            art_style,
            panels
        )

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

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
                        "panel_number": {
                            "type": "integer"
                        },
                        "title": {
                            "type": "string"
                        },
                        "scene_description": {
                            "type": "string"
                        },
                        "image_prompt": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "panel_number",
                        "title",
                        "scene_description",
                        "image_prompt"
                    ]
                }
            }
        },
        "required": ["panels"]
    }

    instruction = f"""
Create exactly {panels} connected comic panels.

Story idea:
{prompt}

Main character:
{character}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Requirements:

1. Create exactly {panels} panels.
2. The story must be continuous.
3. Keep the same main character throughout.
4. Maintain visual continuity.
5. Each panel needs:
   - panel_number
   - title
   - scene_description
   - image_prompt
6. Image prompts must describe visual scenes.
7. Do not put dialogue text inside image prompts.
8. Return ONLY JSON.
"""

    # Try the configured model first
    models_to_try = [
        GEMINI_OUTLINE_MODEL,
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite"
    ]

    last_error = None

    for model_name in models_to_try:

        try:
            print(
                f"[ComicCraft] Trying Gemini model: "
                f"{model_name}"
            )

            response = client.models.generate_content(
                model=model_name,
                contents=instruction,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.9
                )
            )

            print(
                f"[ComicCraft] Gemini success: "
                f"{model_name}"
            )

            return ComicOutline.model_validate_json(
                response.text
            )

        except Exception as error:
            last_error = error

            print(
                f"[ComicCraft] Gemini failed: "
                f"{model_name}"
            )
            print(error)

            # Try next model
            continue

    raise RuntimeError(
        "All Gemini outline models failed. "
        f"Last error: {last_error}"
    )