"""Repository for Quotes and Actuarial Calculations."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendation import Quote
from app.repositories.base import BaseRepository


class QuoteRepository(BaseRepository[Quote]):
    def __init__(self, session: AsyncSession):
        super().__init__(Quote, session)

    async def get_by_quote_number(self, quote_number: str) -> Optional[Quote]:
        stmt = (
            select(Quote)
            .where(Quote.quote_number == quote_number)
            .options(
                selectinload(Quote.product),
                selectinload(Quote.configuration),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, quote_id: str) -> Optional[Quote]:
        stmt = (
            select(Quote)
            .where(Quote.id == quote_id)
            .options(
                selectinload(Quote.product),
                selectinload(Quote.configuration),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_customer(self, customer_id: str) -> Sequence[Quote]:
        stmt = (
            select(Quote)
            .where(Quote.customer_id == customer_id)
            .options(
                selectinload(Quote.product),
                selectinload(Quote.configuration),
            )
            .order_by(Quote.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
