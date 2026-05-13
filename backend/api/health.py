"""
Health check router — system status and diagnostics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter

from backend.config.settings import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }