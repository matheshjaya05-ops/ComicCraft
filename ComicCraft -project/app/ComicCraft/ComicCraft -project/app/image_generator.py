from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont
from huggingface_hub import InferenceClient
from .config import HF_TOKEN, HF_IMAGE_MODEL, HF_PROVIDER, USE_MOCK_AI

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "static" / "panels"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def _safe_name(text):
    text = re.sub(r"[^a-zA-Z0-9_-]+", "-", text).strip("-").lower()
    return text[:60] or "panel"

def _mock_image(prompt, path, panel_number):
    # Offline fallback so the app can be tested without AI credentials.
    img = Image.new("RGB", (1024, 1024), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, 984, 984), outline="black", width=8)
    draw.text((70, 70), f"ComicCraft Panel {panel_number}", fill="black")
    draw.text((70, 140), "Offline preview", fill="black")
    draw.text((70, 210), prompt[:220], fill="black")
    img.save(path, format="PNG")

def generate_image(prompt: str, panel_number: int):
    filename = f"panel-{panel_number}-{_safe_name(prompt)}.png"
    path = OUTPUT_DIR / filename
    if USE_MOCK_AI or not HF_TOKEN:
        _mock_image(prompt, path, panel_number)
        return f"/static/panels/{filename}"

    client = InferenceClient(provider=HF_PROVIDER, api_key=HF_TOKEN)
    image = client.text_to_image(
        prompt=prompt,
        model=HF_IMAGE_MODEL,
        negative_prompt="blurry, distorted anatomy, extra limbs, watermark, logo, readable text, duplicate character",
    )
    image.save(path)
    return f"/static/panels/{filename}"
