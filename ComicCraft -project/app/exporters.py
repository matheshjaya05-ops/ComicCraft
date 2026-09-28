from pathlib import Path
from datetime import datetime
import re

from fpdf import FPDF
from PIL import Image

from .config import BASE_DIR

EXPORT_DIR = BASE_DIR / "static" / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(text):
    if text is None:
        return ""

    text = str(text)

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "…": "...",
        "•": "-",
        "→": "->",
        "←": "<-",
        "✨": "",
        "🚀": "",
        "🎉": "",
        "🔥": "",
        "😊": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Convert to FPDF-compatible characters
    text = text.encode("latin-1", "replace").decode("latin-1")

    # Break extremely long words
    text = re.sub(r"(\S{35})", r"\1 ", text)

    return text.strip()


def write_text(pdf, text, height=7):
    """
    Safely write text from the left margin.
    """

    text = clean_text(text)

    # Always reset horizontal position
    pdf.set_x(pdf.l_margin)

    if text:
        pdf.multi_cell(
            0,
            height,
            text
        )


def get_image_path(image_url):
    return BASE_DIR / image_url.lstrip("/")


def save_pdf(layout):

    filename = (
        "comiccraft-"
        f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
        ".pdf"
    )

    pdf_path = EXPORT_DIR / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_margins(
        left=15,
        top=15,
        right=15
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        # =================================
        # PANEL TITLE
        # =================================

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        title = (
            f"Panel {panel['panel_number']}: "
            f"{panel['title']}"
        )

        write_text(
            pdf,
            title,
            10
        )

        pdf.ln(3)

        # =================================
        # IMAGE
        # =================================

        image_path = get_image_path(
            panel["image_path"]
        )

        if image_path.exists():

            with Image.open(image_path) as image:
                width, height = image.size

            max_width = 180
            max_height = 100

            scale = min(
                max_width / width,
                max_height / height
            )

            display_width = width * scale
            display_height = height * scale

            x = (
                210 - display_width
            ) / 2

            # Make sure image stays inside page
            x = max(15, x)

            pdf.image(
                str(image_path),
                x=x,
                y=pdf.get_y(),
                w=display_width,
                h=display_height
            )

            # IMPORTANT:
            # Reset X position after image
            pdf.set_x(pdf.l_margin)

            pdf.set_y(
                pdf.get_y()
                + display_height
                + 8
            )

        # =================================
        # SCENE
        # =================================

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        write_text(
            pdf,
            panel["scene_description"],
            6
        )

        pdf.ln(2)

        # =================================
        # CAPTION
        # =================================

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        write_text(
            pdf,
            "Caption:",
            6
        )

        pdf.set_font(
            "Helvetica",
            "",
            10
        )

        write_text(
            pdf,
            panel["caption"],
            6
        )

        pdf.ln(2)

        # =================================
        # NARRATION
        # =================================

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        write_text(
            pdf,
            "Narration:",
            6
        )

        pdf.set_font(
            "Helvetica",
            "",
            10
        )

        write_text(
            pdf,
            panel["narration"],
            6
        )

        pdf.ln(2)

        # =================================
        # DIALOGUE
        # =================================

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        write_text(
            pdf,
            "Dialogue:",
            6
        )

        pdf.set_font(
            "Helvetica",
            "",
            10
        )

        write_text(
            pdf,
            panel["dialogue"],
            6
        )

    # =================================
    # SAVE
    # =================================

    pdf.output(
        str(pdf_path)
    )

    return f"/static/exports/{filename}"