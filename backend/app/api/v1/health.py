"""Health and readiness endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.schemas.common import APIResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=APIResponse[dict])
async def health_check():
    """Basic service health check."""
    return APIResponse(
        data={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
        }
    )


@router.get("/db", response_model=APIResponse[dict])
async def database_health_check(session: AsyncSession = Depends(get_db)):
    """Database connectivity and WAL mode verification check."""
    result = await session.execute(text("SELECT 1"))
    one = result.scalar_one()

    # Check WAL mode
    wal_result = await session.execute(text("PRAGMA journal_mode"))
    journal_mode = wal_result.scalar_one()

    # Check foreign keys
    fk_result = await session.execute(text("PRAGMA foreign_keys"))
    foreign_keys = fk_result.scalar_one()

    return APIResponse(
        data={
            "database": "sqlite",
            "connection": "ok" if one == 1 else "failed",
            "journal_mode": str(journal_mode).lower(),
            "foreign_keys_enabled": bool(foreign_keys),
        }
    )

