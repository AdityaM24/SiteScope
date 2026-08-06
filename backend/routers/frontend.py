"""
Static frontend serving.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

FRONTEND_PATH = Path(__file__).parent.parent.parent / "frontend" / "index.html"


@router.get("/", include_in_schema=False)
async def serve_frontend():
    if FRONTEND_PATH.exists():
        return FileResponse(FRONTEND_PATH)
    return {"message": "Frontend not found"}
