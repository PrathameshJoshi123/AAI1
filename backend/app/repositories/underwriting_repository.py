"""Repository for Underwriting Cases, Reviews, and Triage Queues."""
from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import Application, ApplicationDocument
from app.models.profile import Advisor, Customer, Underwriter
from app.models.recommendation import Quote
from app.models.underwriting import CaseNote, UnderwritingCase, UnderwritingReview
from app.repositories.base import BaseRepository


class UnderwritingRepository(BaseRepository[UnderwritingCase]):
    def __init__(self, session: AsyncSession):
        super().__init__(UnderwritingCase, session)

    async def get_by_case_number(self, case_number: str) -> Optional[UnderwritingCase]:
        stmt = (
            select(UnderwritingCase)
            .where(UnderwritingCase.case_number == case_number)
            .options(
                selectinload(UnderwritingCase.reviews).selectinload(UnderwritingReview.reviewer),
                selectinload(UnderwritingCase.application),
                selectinload(UnderwritingCase.customer).selectinload(Customer.user),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_case_number_full(self, case_number: str) -> Optional[UnderwritingCase]:
        stmt = (
            select(UnderwritingCase)
            .where(UnderwritingCase.case_number == case_number)
            .options(
                selectinload(UnderwritingCase.reviews).selectinload(UnderwritingReview.reviewer),
                selectinload(UnderwritingCase.case_notes).selectinload(CaseNote.author),
                selectinload(UnderwritingCase.customer).selectinload(Customer.user),
                selectinload(UnderwritingCase.assigned_advisor).selectinload(Advisor.user),
                selectinload(UnderwritingCase.assigned_underwriter).selectinload(Underwriter.user),
                selectinload(UnderwritingCase.application).selectinload(Application.quote),
                selectinload(UnderwritingCase.application).selectinload(Application.product),
                selectinload(UnderwritingCase.application).selectinload(Application.documents),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_full(self, case_id: str) -> Optional[UnderwritingCase]:
        stmt = (
            select(UnderwritingCase)
            .where(UnderwritingCase.id == case_id)
            .options(
                selectinload(UnderwritingCase.reviews).selectinload(UnderwritingReview.reviewer),
                selectinload(UnderwritingCase.case_notes).selectinload(CaseNote.author),
                selectinload(UnderwritingCase.customer).selectinload(Customer.user),
                selectinload(UnderwritingCase.assigned_advisor).selectinload(Advisor.user),
                selectinload(UnderwritingCase.assigned_underwriter).selectinload(Underwriter.user),
                selectinload(UnderwritingCase.application).selectinload(Application.quote),
                selectinload(UnderwritingCase.application).selectinload(Application.product),
                selectinload(UnderwritingCase.application).selectinload(Application.documents),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_triage(
        self,
        advisor_id: Optional[str] = None,
        underwriter_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        risk_rating: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[UnderwritingCase]:
        stmt = (
            select(UnderwritingCase)
            .options(
                selectinload(UnderwritingCase.customer).selectinload(Customer.user),
                selectinload(UnderwritingCase.assigned_advisor).selectinload(Advisor.user),
                selectinload(UnderwritingCase.assigned_underwriter).selectinload(Underwriter.user),
                selectinload(UnderwritingCase.application).selectinload(Application.quote),
                selectinload(UnderwritingCase.application).selectinload(Application.product),
                selectinload(UnderwritingCase.reviews),
            )
        )
        if advisor_id:
            stmt = stmt.where(UnderwritingCase.assigned_advisor_id == advisor_id)
        if underwriter_id:
            stmt = stmt.where(UnderwritingCase.assigned_underwriter_id == underwriter_id)
        if status:
            stmt = stmt.where(UnderwritingCase.status == status)
        if priority:
            stmt = stmt.where(UnderwritingCase.priority == priority)
        if risk_rating:
            stmt = stmt.where(UnderwritingCase.risk_rating == risk_rating)

        # Order by urgent/high priority first, then SLA deadline
        stmt = stmt.order_by(
            UnderwritingCase.sla_deadline.asc().nullslast(),
            UnderwritingCase.created_at.desc(),
        ).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_for_advisor(self, advisor_id: str) -> Sequence[UnderwritingCase]:
        return await self.list_triage(advisor_id=advisor_id)

    async def list_for_underwriter(self, underwriter_id: Optional[str] = None) -> Sequence[UnderwritingCase]:
        return await self.list_triage(underwriter_id=underwriter_id)

    async def count_by_status(self, advisor_id: Optional[str] = None, underwriter_id: Optional[str] = None) -> dict:
        stmt = select(UnderwritingCase.status, func.count(UnderwritingCase.id)).group_by(UnderwritingCase.status)
        if advisor_id:
            stmt = stmt.where(UnderwritingCase.assigned_advisor_id == advisor_id)
        elif underwriter_id:
            stmt = stmt.where(UnderwritingCase.assigned_underwriter_id == underwriter_id)
        res = await self.session.execute(stmt)
        return dict(res.all())

    async def count_sla_at_risk(self, threshold_time: datetime) -> int:
        stmt = select(func.count(UnderwritingCase.id)).where(
            UnderwritingCase.status.in_(["assigned", "in_review"]),
            UnderwritingCase.sla_deadline <= threshold_time,
        )
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def add_review(self, review: UnderwritingReview) -> UnderwritingReview:
        self.session.add(review)
        await self.session.flush()
        return review
