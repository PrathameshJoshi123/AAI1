"""FastAPI Application Entrypoint for PS-21."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestContextMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan events."""
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    try:
        from app.core.database import AsyncSessionLocal
        from app.ai.agents.registry import agent_registry
        import app.ai.agents  # noqa: F401
        async with AsyncSessionLocal() as session:
            await agent_registry.sync_with_database(session)
    except Exception as e:
        logger.warning(f"Initial agent DB synchronization deferred: {e}")

    # Start the background follow-up & notification event loop (every 5 seconds)
    scheduler_task = None
    try:
        import asyncio
        from app.services.notification_scheduler import (
            start_notification_scheduler,
            stop_notification_scheduler,
        )
        scheduler_task = asyncio.create_task(start_notification_scheduler(interval_seconds=5))
    except Exception as e:
        logger.error(f"Failed to start notification scheduler: {e}")

    yield

    if scheduler_task:
        from app.services.notification_scheduler import stop_notification_scheduler
        await stop_notification_scheduler(scheduler_task)

    logger.info("Shutting down application cleanly.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Conversational Insurance Acquisition & Onboarding Platform Backend API",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom context middleware (Request ID, timing)
app.add_middleware(RequestContextMiddleware)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }

