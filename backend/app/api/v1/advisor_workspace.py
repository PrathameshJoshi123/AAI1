"""Advisor and Underwriter Workspace Endpoints."""
from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_roles
from app.models.auth import User
from app.schemas.advisor import WorkspaceDashboardData
from app.schemas.common import APIResponse
from app.services.advisor_workspace_service import AdvisorWorkspaceService
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/advisor/workspace", tags=["Advisor Workspace"])


@router.get("/dashboard", response_model=APIResponse[WorkspaceDashboardData])
async def get_workspace_dashboard(
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve full workspace dashboard data including real-time KPI counters and urgent action tasks."""
    svc = AdvisorWorkspaceService(session)
    data = await svc.get_dashboard_data(current_user)
    return APIResponse(data=data)


@router.get("/timeline", response_model=APIResponse[List[Dict[str, Any]]])
async def get_enterprise_activity_timeline(
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve cross-domain enterprise audit and activity feed."""
    timeline_svc = TimelineService(session)
    events = await timeline_svc.get_recent_enterprise_timeline()
    return APIResponse(data=events)
