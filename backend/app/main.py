"""FastAPI entrypoint for the F1 race engineering backend."""

from __future__ import annotations

from fastapi import FastAPI

from backend.app.api.routes import router as api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="F1 Race Engineering Backend",
        version="0.1.0",
        description="Backend API for deterministic race strategy simulation and engineering analysis.",
    )
    app.include_router(api_router)
    return app


app = create_app()
