from pathlib import Path
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .models import ProvisionRequest
from .provisioning import build_provisioning
from .settings import settings

app = FastAPI(title="Simple VoIP Provisioner", version="1.0.0")
templates = Jinja2Templates(directory="app/templates")

settings.firmware_root.mkdir(parents=True, exist_ok=True)
settings.configs_root.mkdir(parents=True, exist_ok=True)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Process-Time"] = f"{time.time() - start:.4f}"
    return response


app.mount("/configs", StaticFiles(directory=str(settings.configs_root)), name="configs")
app.mount("/firmware", StaticFiles(directory=str(settings.firmware_root)), name="firmware")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, bool]:
    return {
        "firmware_root_exists": Path(settings.firmware_root).exists(),
        "configs_root_exists": Path(settings.configs_root).exists(),
    }


@app.post("/api/provision")
def provision(request: ProvisionRequest):
    try:
        return build_provisioning(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
