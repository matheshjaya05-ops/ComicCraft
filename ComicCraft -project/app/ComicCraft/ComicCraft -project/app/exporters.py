from pathlib import Path
from datetime import datetime
from fpdf import FPDF
import requests
from PIL import Image
from .config import BASE_DIR

EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def _image_path(url):
    return BASE_DIR / url.lstrip("/").replace("/", "/")

def save_pdf(layout):
    filename = f"comiccraft-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.pdf"
    path = EXPORT_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.multi_cell(0, 10, f"Panel {panel['panel_number']}: {panel['title']}")
        pdf.ln(2)

        img_path = _image_path(panel["image_path"])
        if img_path.exists():
            with Image.open(img_path) as im:
                w, h = im.size
            max_w = 180
            max_h = 105
            scale = min(max_w / w, max_h / h)
            pdf.image(str(img_path), x=(210 - w*scale)/2, y=35, w=w*scale, h=h*scale)
            pdf.ln(112)

        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, panel["scene_description"])
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, f"Caption: {panel['caption']}")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, f"Narration: {panel['narration']}")
        pdf.multi_cell(0, 7, f"Dialogue: {panel['dialogue']}")

    pdf.output(str(path))
    return f"/static/exports/{filename}"
