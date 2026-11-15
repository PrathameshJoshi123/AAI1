"""Admin Agent Control Centre API Router."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import (
    AgentTelemetryResponse,
    AgentStatusUpdateRequest,
    AgentExecutionLogsResponse,
)
from app.services.agent_control_service import AgentControlService

router = APIRouter(prefix="/admin/agents", tags=["Admin - Agent Control Centre"])


@router.get("", response_model=List[AgentTelemetryResponse])
async def list_agents(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[AgentTelemetryResponse]:
    """List all AI agents with live telemetry, status, and latency."""
    service = AgentControlService(session)
    return await service.list_agent_telemetry()


@router.patch("/{agent_name}/status", response_model=AgentTelemetryResponse)
async def update_agent_status(
    agent_name: str,
    req: AgentStatusUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> AgentTelemetryResponse:
    """Toggle agent status (active, paused, disabled) with runtime backend enforcement."""
    service = AgentControlService(session)
    return await service.update_agent_status(agent_name, req.status, admin_user_id=current_user.id)


@router.get("/{agent_name}/executions", response_model=AgentExecutionLogsResponse)
async def get_agent_executions(
    agent_name: str,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> AgentExecutionLogsResponse:
    """Retrieve chronological execution traces and error telemetry for a specific agent."""
    service = AgentControlService(session)
    return await service.get_agent_execution_logs(agent_name, limit=limit)

