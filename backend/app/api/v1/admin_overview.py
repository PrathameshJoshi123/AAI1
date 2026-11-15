"""Admin Overview API Router."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import ExecutiveMetricsResponse, RecentActivityResponse, AdminCustomerItem
from app.services.admin_overview_service import AdminOverviewService

router = APIRouter(prefix="/admin/overview", tags=["Admin - Overview"])


@router.get("/metrics", response_model=ExecutiveMetricsResponse)
async def get_overview_metrics(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> ExecutiveMetricsResponse:
    """Retrieve real-time database-calculated executive KPI metrics."""
    service = AdminOverviewService(session)
    return await service.get_executive_metrics()


@router.get("/activity-stream", response_model=RecentActivityResponse)
async def get_activity_stream(
    limit: int = Query(15, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> RecentActivityResponse:
    """Retrieve the recent real-time activity stream from audit logs."""
    service = AdminOverviewService(session)
    return await service.get_recent_activity_pulse(limit=limit)


@router.get("/customers", response_model=List[AdminCustomerItem])
async def list_admin_customers(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[AdminCustomerItem]:
    """Retrieve all customer master profiles with onboarding stages."""
    service = AdminOverviewService(session)
    return await service.list_customers()
