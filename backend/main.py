"""
Saṃśodhakaḥ — FastAPI Application Factory

Evidence-grounded scientific research intelligence system.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config.settings import settings
from backend.utils.logging import setup_logging
from backend.retrieval.scholarly import initialize_scholarly_retrieval

# API routers
from backend.api.health import router as health_router
from backend.api.documents import router as documents_router
from backend.api.retrieval import router as retrieval_router
from backend.api.drafting import router as drafting_router
from backend.api.verification import router as verification_router
from backend.api.export import router as export_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    # Startup
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"(debug={settings.debug})"
    )
    settings.ensure_directories()
    
    # Initialize scholarly retrieval system
    initialize_scholarly_retrieval()
    
    yield
    # Shutdown
    logger.info(f"{settings.app_name} shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Evidence-grounded scientific research intelligence system",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # ── Middleware ──────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(documents_router)
    app.include_router(retrieval_router)
    app.include_router(drafting_router)
    app.include_router(verification_router)
    app.include_router(export_router)

    # ── Root endpoint ──────────────────────────────────────────
    @app.get("/")
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "endpoints": {
                "health": "/health",
                "documents": "/api/documents",
                "retrieval": "/api/retrieval",
                "drafting": "/api/drafting",
                "verification": "/api/verification",
                "export": "/api/export",
            },
        }

    return app


# Application instance
app = create_app()


def run() -> None:
    """Run the development server."""
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level,
    )


if __name__ == "__main__":
    run()
