"""Prospect and lead pipeline data access repository."""
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple
from sqlalchemy import desc, asc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.audit import ConsentRecord
from app.models.profile import Advisor
from app.models.prospect import BehavioralSignal, LeadScore, LeadSource, Prospect
from app.repositories.base import BaseRepository


class ProspectRepository(BaseRepository[Prospect]):
    def __init__(self, session: AsyncSession):
        super().__init__(Prospect, session)

    async def get_by_email(self, email: str) -> Optional[Prospect]:
        stmt = select(Prospect).where(func.lower(Prospect.email) == email.lower().strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[Prospect]:
        stmt = select(Prospect).where(Prospect.phone == phone.strip())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_detail(self, prospect_id: str) -> Optional[Prospect]:
        stmt = (
            select(Prospect)
            .where(Prospect.id == prospect_id)
            .options(
                selectinload(Prospect.source),
                selectinload(Prospect.assigned_advisor).selectinload(Advisor.user),
                selectinload(Prospect.signals),
                selectinload(Prospect.lead_scores),
                selectinload(Prospect.consents),
                selectinload(Prospect.follow_ups),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_and_filter(
        self,
        query: Optional[str] = None,
        status_filter: Optional[List[str]] = None,
        segment_filter: Optional[List[str]] = None,
        source_id: Optional[int] = None,
        assigned_advisor_id: Optional[str] = None,
        unassigned_only: bool = False,
        min_score: Optional[float] = None,
        max_score: Optional[float] = None,
        consented_only: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "last_activity_at",
        sort_order: str = "desc",
    ) -> Tuple[Sequence[Prospect], int]:
        stmt = select(Prospect).options(
            selectinload(Prospect.source),
            selectinload(Prospect.assigned_advisor).selectinload(Advisor.user),
            selectinload(Prospect.lead_scores),
            selectinload(Prospect.consents),
        )

        filters = []

        if query:
            q_clean = f"%{query.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(Prospect.name).like(q_clean),
                    func.lower(Prospect.email).like(q_clean),
                    Prospect.phone.like(q_clean),
                    Prospect.id.like(q_clean),
                )
            )

        if status_filter:
            filters.append(Prospect.status.in_(status_filter))

        if segment_filter:
            filters.append(Prospect.segment.in_(segment_filter))

        if source_id is not None:
            filters.append(Prospect.source_id == source_id)

        if unassigned_only:
            filters.append(Prospect.assigned_advisor_id.is_(None))
        elif assigned_advisor_id:
            filters.append(Prospect.assigned_advisor_id == assigned_advisor_id)

        if date_from:
            filters.append(Prospect.created_at >= date_from)
        if date_to:
            filters.append(Prospect.created_at <= date_to)

        if consented_only:
            stmt = stmt.join(
                ConsentRecord,
                (ConsentRecord.prospect_id == Prospect.id)
                & (ConsentRecord.consent_type == "marketing_contact")
                & (ConsentRecord.revoked_at.is_(None)),
            )

        if filters:
            stmt = stmt.where(*filters)

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        # Sorting
        sort_col = getattr(Prospect, sort_by, Prospect.last_activity_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_col))
        else:
            stmt = stmt.order_by(desc(sort_col))

        stmt = stmt.offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    async def get_advisor_leads(
        self,
        advisor_id: str,
        status_filter: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[Sequence[Prospect], int]:
        stmt = (
            select(Prospect)
            .where(Prospect.assigned_advisor_id == advisor_id)
            .options(
                selectinload(Prospect.source),
                selectinload(Prospect.lead_scores),
                selectinload(Prospect.consents),
                selectinload(Prospect.follow_ups),
            )
        )
        if status_filter:
            stmt = stmt.where(Prospect.status.in_(status_filter))

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.session.execute(count_stmt)
        total = count_res.scalar_one()

        stmt = stmt.order_by(desc(Prospect.last_activity_at)).offset(skip).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    async def get_pipeline_kpis(self) -> Dict[str, Any]:
        """Aggregate high-level pipeline counts for admin dashboard."""
        total_stmt = select(func.count(Prospect.id))
        total = (await self.session.execute(total_stmt)).scalar_one()

        status_stmt = select(Prospect.status, func.count(Prospect.id)).group_by(Prospect.status)
        status_counts = dict((await self.session.execute(status_stmt)).all())

        segment_stmt = select(Prospect.segment, func.count(Prospect.id)).group_by(Prospect.segment)
        segment_counts = dict((await self.session.execute(segment_stmt)).all())

        unassigned_stmt = select(func.count(Prospect.id)).where(Prospect.assigned_advisor_id.is_(None))
        unassigned_count = (await self.session.execute(unassigned_stmt)).scalar_one()

        return {
            "total_prospects": total,
            "status_breakdown": status_counts,
            "segment_breakdown": segment_counts,
            "unassigned_leads": unassigned_count,
        }

