"""
Agent Factory IDE — FastAPI Backend
=====================================
Entry point (run from project root):
    python -m backend.main

Or directly from the backend/ folder:
    python main.py
"""
from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager

# ── project-root bootstrap ────────────────────────────────────────────────────
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

from backend.db import init_db
from backend.api.routes       import router as _legacy_router
from backend.api.ws           import ws_router as _legacy_ws_router
from backend.routers.pipeline import router as pipeline_router
from backend.routers.ws       import router as ws_router
from backend.routers.terminal import router as terminal_router
from backend.routers.files    import router as files_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup ──────────────────────────────────────────────────────────────
    await init_db()
    logger.info("Agent Factory backend ready (log_level=%s)", settings.log_level)
    yield
    # ── shutdown (add cleanup here if needed) ────────────────────────────────


app = FastAPI(
    title="Agent Factory IDE API",
    version="2.0.0",
    description="AI agent orchestration platform — Phase 2",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(_legacy_router,  prefix="/api")
app.include_router(_legacy_ws_router)
app.include_router(pipeline_router, prefix="/api")
app.include_router(ws_router)
app.include_router(terminal_router)
app.include_router(files_router,    prefix="/api")


@app.get("/health", tags=["meta"])
async def health() -> dict:
    return {"status": "ok", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        # Only watch real source
        reload_dirs=["backend", "agent_factory", "config"],
        log_level="info",
    )
