"""
GanitMitra — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings
from app.core.database import engine, Base
from app.core.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    # Database tables are created via Alembic migrations
    # Qdrant collection initialization happens in RAG module
    yield
    # Shutdown
    await engine.dispose()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Multilingual Math Learning Companion",
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gzip
    app.add_middleware(GZipMiddleware, minimum_size=500)

    # Prometheus metrics
    if settings.app_env != "production":
        Instrumentator().instrument(app).expose(app, include_in_schema=False)

    # Exception handlers
    register_exception_handlers(app)

    # Register routers
    from app.api.v1.auth import router as auth_router
    from app.api.v1.students import router as students_router
    from app.api.v1.tutoring import router as tutoring_router
    from app.api.v1.practice import router as practice_router
    from app.api.v1.progress import router as progress_router
    from app.api.v1.topics import router as topics_router
    from app.api.v1.reports import router as reports_router
    from app.api.v1.voice import router as voice_router
    from app.api.v1.achievements import router as achievements_router

    app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(students_router, prefix="/api/v1/students", tags=["students"])
    app.include_router(tutoring_router, prefix="/api/v1/tutoring", tags=["tutoring"])
    app.include_router(practice_router, prefix="/api/v1/practice", tags=["practice"])
    app.include_router(progress_router, prefix="/api/v1/progress", tags=["progress"])
    app.include_router(topics_router, prefix="/api/v1/topics", tags=["topics"])
    app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
    app.include_router(voice_router, prefix="/api/v1/voice", tags=["voice"])
    app.include_router(achievements_router, prefix="/api/v1/achievements", tags=["achievements"])

    # Health check
    @app.get("/api/v1/health", tags=["health"])
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.app_env.value,
        }

    return app


app = create_application()
