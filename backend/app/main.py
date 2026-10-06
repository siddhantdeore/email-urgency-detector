"""FastAPI Main Application Entrypoint.

Cognitive Email Urgency Detector & Intelligent Priority Assistant.
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import sys
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from backend.app.api.routes import router as api_router
from backend.app.config import MODELS_DIR, URGENCY_MODEL_PATH
from backend.app.ml.train import train_models

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not URGENCY_MODEL_PATH.exists():
        print("Models not found on startup. Automatically triggering training...")
        train_models()
    yield

app = FastAPI(
    title="Cognitive Email Urgency Detector & Intelligent Priority Assistant",
    description=(
        "Production-grade Cognitive Computing and NLP system for intelligent email "
        "urgency detection, intent classification, multi-factor reasoning, and explainable AI."
    ),
    version="1.0.0",
    lifespan=lifespan,
)



# Enable CORS for local dev / frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api prefix and root aliases

app.include_router(api_router, prefix="/api", tags=["Cognitive AI"])
app.include_router(api_router, tags=["Root Aliases"])

# Mount Frontend static assets
FRONTEND_DIR = WORKSPACE_ROOT / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    @app.get("/dashboard", include_in_schema=False)
    def serve_dashboard():
        return FileResponse(FRONTEND_DIR / "dashboard.html")

    @app.get("/model", include_in_schema=False)
    def serve_model():
        return FileResponse(FRONTEND_DIR / "model.html")
