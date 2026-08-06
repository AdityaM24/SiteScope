"""
GEO Auditor — FastAPI Application Entry Point

Serves the API (FastAPI routers) AND the built React frontend
(static files + SPA fallback) from a single process, so the whole
app deploys as one service on Railway / Render.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings, setup_logging
from .routers import health, audit

setup_logging()

app = FastAPI(
    title="GEO Auditor",
    description="AI Citation Readiness Auditor — Checks if a site is optimized for AI search engines.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API routes (registered before the SPA fallback so they take priority) ──
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])

# ── Serve the built React frontend ─────────────────────────────────────────
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
ASSETS_DIR = FRONTEND_DIST / "assets"

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend not built. Run: cd frontend && npm run build"}


@app.api_route("/{path:path}", methods=["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
async def spa_fallback(path: str):
    """SPA fallback — any non-API, non-asset route returns index.html."""
    # Never swallow API or asset paths that should 404/route normally
    if path.startswith("api/") or path.startswith("health") or path.startswith("docs") or path.startswith("redoc"):
        return FileResponse(FRONTEND_DIST / "index.html", status_code=200)
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend not found"}, 404
