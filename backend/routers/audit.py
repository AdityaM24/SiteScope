"""
Audit endpoint — POST /api/v1/audit
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..audit_pipeline import run_audit
from ..models import AuditRequest

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/audit",
    summary="Run GEO Audit",
    description="Submit a public URL for a complete AI-citation-readiness audit.",
    responses={
        200: {"description": "Audit report"},
        400: {"description": "Invalid URL"},
        422: {"description": "Unsupported website"},
        500: {"description": "Crawler/server error"},
    },
)
async def run_audit_endpoint(request: AuditRequest) -> dict:
    """Run a GEO audit on the provided URL."""
    try:
        report = await run_audit(request)
        return {
            "success": True,
            "message": "Audit completed successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": report,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Audit failed for %s: %s", request.url, e, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audit failed: {e}")
