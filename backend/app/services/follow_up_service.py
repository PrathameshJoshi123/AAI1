"""Service for Follow-up Management."""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.auth import User
from app.models.profile import Advisor, Customer
from app.models.prospect import Prospect
from app.models.system import FollowUp
from app.repositories.follow_up_repository import FollowUpRepository
from app.schemas.follow_up import FollowUpCreate, FollowUpRead, FollowUpUpdate


class FollowUpService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FollowUpRepository(session)

    async def list_follow_ups(
        self,
        current_user: User,
        status: Optional[str] = None,
        due_before: Optional[datetime] = None,
    ) -> List[FollowUpRead]:
        user_roles = [r.name for r in current_user.roles]
        advisor_id = current_user.advisor.id if "Advisor" in user_roles and current_user.advisor else None
        if any(r in ("Admin", "Owner", "Underwriter") for r in user_roles):
            advisor_id = None

        items = await self.repo.list_for_advisor(
            advisor_id=advisor_id,
            status=status,
            due_before=due_before,
        )

        out = []
        for fu in items:
            t_name = None
            t_contact = None
            if fu.customer and fu.customer.user:
                t_name = fu.customer.user.full_name
                t_contact = fu.customer.user.phone_number or fu.customer.user.email
            elif fu.prospect:
                t_name = fu.prospect.full_name
                t_contact = fu.prospect.phone or fu.prospect.email

            out.append(
                FollowUpRead(
                    id=fu.id,
                    customer_id=fu.customer_id,
                    prospect_id=fu.prospect_id,
                    assigned_advisor_id=fu.assigned_advisor_id,
                    target_name=t_name,
                    target_contact=t_contact,
                    due_date=fu.due_date,
                    channel=fu.channel,
                    status=fu.status,
                    priority=fu.priority,
                    notes=fu.notes,
                    created_at=fu.created_at,
                    updated_at=fu.updated_at,
                )
            )
        return out

    async def create_follow_up(self, data: FollowUpCreate, current_user: User) -> FollowUpRead:
        user_roles = [r.name for r in current_user.roles]
        advisor_id = data.assigned_advisor_id
        if not advisor_id:
            if current_user.advisor:
                advisor_id = current_user.advisor.id
            else:
                # pick current user if has advisor profile or error
                raise PermissionDeniedException("An assigned_advisor_id must be provided.")

        fu = FollowUp(
            customer_id=data.customer_id,
            prospect_id=data.prospect_id,
            assigned_advisor_id=advisor_id,
            due_date=data.due_date,
            channel=data.channel,
            priority=data.priority,
            status="pending",
            notes=data.notes,
        )
        self.session.add(fu)
        await self.session.commit()
        await self.session.refresh(fu)

        return FollowUpRead(
            id=fu.id,
            customer_id=fu.customer_id,
            prospect_id=fu.prospect_id,
            assigned_advisor_id=fu.assigned_advisor_id,
            target_name=None,
            target_contact=None,
            due_date=fu.due_date,
            channel=fu.channel,
            status=fu.status,
            priority=fu.priority,
            notes=fu.notes,
            created_at=fu.created_at,
            updated_at=fu.updated_at,
        )

    async def update_status(self, follow_up_id: int, data: FollowUpUpdate, current_user: User) -> FollowUpRead:
        fu = await self.repo.get_by_id(follow_up_id)
        if not fu:
            raise EntityNotFoundException("Follow-up not found.")

        if data.status:
            fu.status = data.status
        if data.notes:
            fu.notes = data.notes
        if data.channel:
            fu.channel = data.channel
        if data.priority:
            fu.priority = data.priority
        if data.due_date:
            fu.due_date = data.due_date

        await self.session.commit()
        await self.session.refresh(fu)

        return FollowUpRead(
            id=fu.id,
            customer_id=fu.customer_id,
            prospect_id=fu.prospect_id,
            assigned_advisor_id=fu.assigned_advisor_id,
            due_date=fu.due_date,
            channel=fu.channel,
            status=fu.status,
            priority=fu.priority,
            notes=fu.notes,
            created_at=fu.created_at,
            updated_at=fu.updated_at,
        )

