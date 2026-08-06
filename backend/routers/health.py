"""
Health check endpoint.
"""
from __future__ import annotations

import time

from fastapi import APIRouter

from ..config import settings
from ..models import HealthResponse

router = APIRouter()

_start_time = time.time()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verify the backend is alive and healthy.",
)
async def health_check() -> HealthResponse:
    uptime = int(time.time() - _start_time)
    return HealthResponse(
        status="healthy",
        version=settings.__class__.__name__.lower(),
        uptime=uptime,
    )
