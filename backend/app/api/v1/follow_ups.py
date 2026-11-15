"""Follow-up Management Endpoints."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_roles
from app.models.auth import User
from app.schemas.common import APIResponse
from app.schemas.follow_up import FollowUpCreate, FollowUpRead, FollowUpUpdate
from app.services.follow_up_service import FollowUpService

router = APIRouter(prefix="/follow-ups", tags=["Follow-ups"])


@router.get("", response_model=APIResponse[List[FollowUpRead]])
async def list_follow_ups(
    status: Optional[str] = Query(None),
    due_before: Optional[datetime] = Query(None),
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """List scheduled follow-up engagements scoped to the advisor or administrative queue."""
    svc = FollowUpService(session)
    items = await svc.list_follow_ups(current_user=current_user, status=status, due_before=due_before)
    return APIResponse(data=items)


@router.post("", response_model=APIResponse[FollowUpRead], status_code=status.HTTP_201_CREATED)
async def schedule_follow_up(
    data: FollowUpCreate,
    current_user: User = Depends(require_roles(["Advisor", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Schedule a new customer follow-up engagement."""
    svc = FollowUpService(session)
    created = await svc.create_follow_up(data, current_user)
    return APIResponse(data=created, message="Follow-up scheduled successfully.")


@router.put("/{id}", response_model=APIResponse[FollowUpRead])
async def update_follow_up(
    id: int,
    data: FollowUpUpdate,
    current_user: User = Depends(require_roles(["Advisor", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Update follow-up status, reschedule due date, or append outcome notes."""
    svc = FollowUpService(session)
    updated = await svc.update_status(id, data, current_user)
    return APIResponse(data=updated, message="Follow-up updated successfully.")

