from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import router

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

(STATIC_DIR / "panels").mkdir(
    parents=True,
    exist_ok=True
)

(STATIC_DIR / "exports").mkdir(
    parents=True,
    exist_ok=True
)

app = FastAPI(
    title="ComicCraft",
    description="AI Comic Story Creator",
    version="1.0.0"
)

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ComicCraft"
    }