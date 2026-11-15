"""Repository for FollowUp operations."""
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Advisor, Customer
from app.models.prospect import Prospect
from app.models.system import FollowUp
from app.repositories.base import BaseRepository


class FollowUpRepository(BaseRepository[FollowUp]):
    def __init__(self, session: AsyncSession):
        super().__init__(FollowUp, session)

    async def list_for_advisor(
        self,
        advisor_id: Optional[str] = None,
        status: Optional[str] = None,
        due_before: Optional[datetime] = None,
    ) -> Sequence[FollowUp]:
        stmt = (
            select(FollowUp)
            .options(
                selectinload(FollowUp.customer).selectinload(Customer.user),
                selectinload(FollowUp.prospect),
                selectinload(FollowUp.assigned_advisor).selectinload(Advisor.user),
            )
            .order_by(FollowUp.due_date.asc())
        )
        if advisor_id:
            stmt = stmt.where(FollowUp.assigned_advisor_id == advisor_id)
        if status:
            stmt = stmt.where(FollowUp.status == status)
        if due_before:
            stmt = stmt.where(FollowUp.due_date <= due_before)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_overdue(self, advisor_id: Optional[str] = None, now: Optional[datetime] = None) -> int:
        from sqlalchemy import func
        if now is None:
            now = datetime.utcnow()
        stmt = select(func.count(FollowUp.id)).where(
            FollowUp.status == "pending",
            FollowUp.due_date < now,
        )
        if advisor_id:
            stmt = stmt.where(FollowUp.assigned_advisor_id == advisor_id)
        res = await self.session.execute(stmt)
        return res.scalar() or 0

