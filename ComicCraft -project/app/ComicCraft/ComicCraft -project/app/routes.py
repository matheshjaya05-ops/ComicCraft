from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from .schemas import PromptRequest
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .exporters import save_pdf
from .config import PANELS

router = APIRouter()

@router.get("/")
async def home(request: Request):
    from .main import templates
    return templates.TemplateResponse("index.html", {"request": request, "panels": PANELS})

def _generate(data: PromptRequest):
    outline = generate_outline(
        data.story_prompt, data.character_name, data.setting,
        data.tone, data.art_style, data.panels
    )
    story = generate_story(outline, data.character_name, data.tone)
    image_paths = [
        generate_image(panel.image_prompt, panel.panel_number)
        for panel in outline.panels
    ]
    layout = build_comic_layout(outline, story, image_paths)
    pdf_path = save_pdf(layout)
    return layout, pdf_path

@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
    panels: int = Form(PANELS),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt.strip(),
            character_name=character_name.strip(),
            setting=setting.strip(),
            tone=tone.strip(),
            art_style=art_style.strip(),
            panels=panels,
        )
        layout, pdf_path = _generate(data)
        from .main import templates
        return templates.TemplateResponse(
            "comic_preview.html",
            {"request": request, "layout": layout, "pdf_path": pdf_path}
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {exc}")

@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):
    try:
        layout, pdf_path = _generate(data)
        return {"success": True, "layout": layout, "pdf_path": pdf_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comic generation failed: {exc}")

@router.get("/export-success")
async def export_success(request: Request, pdf: str = ""):
    from .main import templates
    return templates.TemplateResponse(
        "export_success.html", {"request": request, "pdf_path": pdf}
    )

@router.get("/test-image")
async def test_image(prompt: str = "A cute fox hero in an enchanted forest, comic book art"):
    try:
        return {"success": True, "image_path": generate_image(prompt, 1)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
