"""Notifications API endpoints."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.core.exceptions import EntityNotFoundException
from app.models.auth import User
from app.models.system import Notification
from app.schemas.common import APIResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationRead(BaseModel):
    id: int
    user_id: str
    title: str
    message: str
    notification_type: str
    is_read: bool
    link_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationSummary(BaseModel):
    unread_count: int
    items: List[NotificationRead]


@router.get("", response_model=APIResponse[NotificationSummary])
async def list_notifications(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve notifications and unread counter for current user."""
    # Count unread
    count_stmt = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    )
    res_count = await session.execute(count_stmt)
    unread_count = res_count.scalar() or 0

    # Get items
    stmt = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(desc(Notification.created_at))
        .limit(limit)
    )
    res = await session.execute(stmt)
    items = res.scalars().all()

    return APIResponse(
        data=NotificationSummary(
            unread_count=unread_count,
            items=[NotificationRead.model_validate(n) for n in items],
        )
    )


@router.put("/{notification_id}/read", response_model=APIResponse[NotificationRead])
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    stmt = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    )
    res = await session.execute(stmt)
    notif = res.scalar_one_or_none()
    if notif:
        notif.is_read = True
        await session.commit()
        await session.refresh(notif)
        return APIResponse(data=NotificationRead.model_validate(notif))
    else:
        raise EntityNotFoundException("Notification not found.")


@router.put("/mark-all-read", response_model=APIResponse[dict])
async def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read for current user."""
    from sqlalchemy import update
    stmt = update(Notification).where(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).values(is_read=True)
    await session.execute(stmt)
    await session.commit()
    return APIResponse(data={"message": "All notifications marked as read."})


@router.get("/scheduler/status", response_model=APIResponse[dict])
async def get_scheduler_status(
    current_user: User = Depends(get_current_user),
):
    """Get the running status, interval, and tick statistics of the notification event loop."""
    from app.services.notification_scheduler import scheduler_state

    return APIResponse(
        data={
            "is_running": scheduler_state.is_running,
            "interval_seconds": scheduler_state.interval_seconds,
            "ticks_count": scheduler_state.ticks_count,
            "total_dispatched": scheduler_state.total_dispatched,
            "last_run_at": scheduler_state.last_run_at.isoformat() if scheduler_state.last_run_at else None,
            "last_run_summary": scheduler_state.last_run_summary,
        }
    )


@router.post("/scheduler/tick", response_model=APIResponse[dict])
async def trigger_scheduler_tick(
    current_user: User = Depends(get_current_user),
):
    """Manually trigger one tick of the background notification event loop immediately."""
    from app.services.notification_scheduler import process_followup_and_system_notifications

    result = await process_followup_and_system_notifications()
    return APIResponse(data=result, message="Notification event loop tick completed.")


@router.post("/test-followup", response_model=APIResponse[dict])
async def create_test_followup(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Create a due follow-up for the current user to verify the 5-second background notification loop."""
    from app.models.profile import Advisor, Customer
    from app.models.system import FollowUp
    from datetime import timezone

    # Locate advisor id if current user is advisor or find default
    advisor = None
    if current_user.advisor:
        advisor = current_user.advisor
    else:
        res = await session.execute(select(Advisor).limit(1))
        advisor = res.scalar_one_or_none()

    if not advisor:
        return APIResponse(
            success=False,
            message="No advisor available in the system to assign follow-up.",
            data={},
        )

    # Locate customer if available
    customer_id = current_user.customer.id if current_user.customer else None

    # Due immediately in the past so the 5s loop picks it up right away
    due_now = datetime.now(timezone.utc)
    test_fu = FollowUp(
        customer_id=customer_id,
        assigned_advisor_id=advisor.id,
        due_date=due_now,
        channel="phone",
        priority="high",
        status="pending",
        notes=f"Automated test follow-up for {current_user.full_name} to test 5-second notification loop.",
    )
    session.add(test_fu)
    await session.commit()
    await session.refresh(test_fu)

    return APIResponse(
        data={
            "follow_up_id": test_fu.id,
            "due_date": test_fu.due_date.isoformat(),
            "assigned_advisor_id": advisor.id,
            "message": "Test follow-up created! The background event loop will dispatch a notification within 5 seconds.",
        },
        message="Test follow-up created successfully.",
    )


