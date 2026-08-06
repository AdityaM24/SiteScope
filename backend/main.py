"""
GEO Auditor — FastAPI Application Entry Point
"""
from __future__ import annotations

import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings, setup_logging
from .routers import health, audit, frontend

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

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(audit.router, prefix="/api/v1", tags=["audit"])
app.include_router(frontend.router, tags=["frontend"])

# Serve frontend at root
@app.get("/", include_in_schema=False)
async def root():
    return await frontend.serve_frontend()
