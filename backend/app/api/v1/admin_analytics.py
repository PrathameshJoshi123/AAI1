"""Admin Business Analytics API Router."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import (
    ChannelPerformanceItem,
    ProductPerformanceItem,
    AdvisorPerformanceItem,
    TurnaroundAnalyticsResponse,
)
from app.services.admin_analytics_service import AdminAnalyticsService

router = APIRouter(prefix="/admin/analytics", tags=["Admin - Analytics"])


@router.get("/channels", response_model=List[ChannelPerformanceItem])
async def get_channel_analytics(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[ChannelPerformanceItem]:
    """Retrieve acquisition channel volume and conversion performance."""
    service = AdminAnalyticsService(session)
    return await service.get_channel_performance()


@router.get("/products", response_model=List[ProductPerformanceItem])
async def get_product_analytics(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[ProductPerformanceItem]:
    """Retrieve quote volumes, applications, and revenue by insurance product."""
    service = AdminAnalyticsService(session)
    return await service.get_product_performance()


@router.get("/advisors", response_model=List[AdvisorPerformanceItem])
async def get_advisor_analytics(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[AdvisorPerformanceItem]:
    """Retrieve individual advisor caseload and conversion benchmarks."""
    service = AdminAnalyticsService(session)
    return await service.get_advisor_performance()


@router.get("/turnaround", response_model=TurnaroundAnalyticsResponse)
async def get_turnaround_times(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> TurnaroundAnalyticsResponse:
    """Retrieve SLA turnaround time benchmarks."""
    service = AdminAnalyticsService(session)
    return await service.get_turnaround_analytics()

