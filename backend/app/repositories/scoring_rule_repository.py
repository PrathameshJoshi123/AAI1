"""Lead scoring rules data access repository."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prospect import LeadScoringRule
from app.repositories.base import BaseRepository


class ScoringRuleRepository(BaseRepository[LeadScoringRule]):
    def __init__(self, session: AsyncSession):
        super().__init__(LeadScoringRule, session)

    async def get_active_rules(self) -> Sequence[LeadScoringRule]:
        stmt = (
            select(LeadScoringRule)
            .where(LeadScoringRule.is_active == True)
            .order_by(LeadScoringRule.category, LeadScoringRule.rule_code)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_code(self, rule_code: str) -> Optional[LeadScoringRule]:
        stmt = select(LeadScoringRule).where(LeadScoringRule.rule_code == rule_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

