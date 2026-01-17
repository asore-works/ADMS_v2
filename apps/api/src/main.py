"""ADMS API - Main entry point"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.db import close_redis_pool
from src.db.session import engine
from src.utils import get_logger, register_exception_handlers, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan handler

    Manages startup and shutdown events.
    """
    # Startup
    setup_logging()
    logger.info("Starting ADMS API v%s", settings.app_version)
    logger.info("Debug mode: %s", settings.debug)

    yield

    # Shutdown
    logger.info("Shutting down ADMS API...")

    # Close database connections
    await engine.dispose()
    logger.info("Database connections closed")

    # Close Redis connections
    await close_redis_pool()
    logger.info("Redis connections closed")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.app_name,
        description="Advanced Drone Management System API",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan,
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }
