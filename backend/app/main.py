"""
GanitMitra — FastAPI Application Entry Point
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.config import settings
from app.core.exceptions import register_exception_handlers

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env.value}")
    logger.info(f"Reasoning provider: {settings.reasoning_provider.value}")
    logger.info(f"OpenAI configured: {settings.is_openai_configured}")
    logger.info(f"DeepSeek configured: {settings.is_deepseek_configured}")
    yield
    # Shutdown
    from app.core.database import engine
    await engine.dispose()
    logger.info("Shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AI-Powered Multilingual Math Learning Companion for Nursery to Class 10",
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

    # Prometheus metrics (optional)
    try:
        from prometheus_fastapi_instrumentator import Instrumentator
        Instrumentator().instrument(app).expose(app, include_in_schema=False)
    except ImportError:
        logger.warning("prometheus_fastapi_instrumentator not installed, skipping metrics")

    # Exception handlers
    register_exception_handlers(app)

    # Register routers with graceful error handling
    _register_routers(app)

    # Health check — always available
    @app.get("/api/v1/health", tags=["health"])
    async def health_check():
        health = {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.app_env.value,
            "reasoning_provider": settings.reasoning_provider.value,
            "timestamp": None,
        }
        return health

    return app


def _register_routers(app: FastAPI):
    """Register all API routers. Gracefully skips any that fail to import."""
    router_specs = [
        ("app.api.v1.auth", "/api/v1/auth", ["auth"]),
        ("app.api.v1.students", "/api/v1/students", ["students"]),
        ("app.api.v1.tutoring", "/api/v1/tutoring", ["tutoring"]),
        ("app.api.v1.practice", "/api/v1/practice", ["practice"]),
        ("app.api.v1.progress", "/api/v1/progress", ["progress"]),
        ("app.api.v1.topics", "/api/v1/topics", ["topics"]),
        ("app.api.v1.reports", "/api/v1/reports", ["reports"]),
        ("app.api.v1.voice", "/api/v1/voice", ["voice"]),
        ("app.api.v1.achievements", "/api/v1/achievements", ["achievements"]),
        ("app.api.v1.tutors", "/api/v1/tutors", ["tutors"]),
        ("app.api.v1.admin", "/api/v1/admin", ["admin"]),
        ("app.api.v1.content", "/api/v1/content", ["content"]),
        ("app.api.v1.notifications", "/api/v1/notifications", ["notifications"]),
    ]

    import importlib

    for module_path, prefix, tags in router_specs:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, "router"):
                app.include_router(module.router, prefix=prefix, tags=tags)
            else:
                logger.warning(f"Module {module_path} has no 'router' attribute")
        except Exception as e:
            logger.warning(f"Failed to register router {module_path}: {e}")
            # Create stub router so URLs don't 404
            from fastapi import APIRouter
            stub = APIRouter()

            @stub.get("")
            async def stub_endpoint():
                return {"status": "not_available", "message": "This service is not configured yet"}

            @stub.get("/{path:path}")
            async def stub_catchall(path: str):
                return {"status": "not_available", "message": f"Service not available: {path}"}

            app.include_router(stub, prefix=prefix, tags=tags)


app = create_application()
