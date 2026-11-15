"""Repository for Applications."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.application import Application
from app.repositories.base import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, session: AsyncSession):
        super().__init__(Application, session)

    async def get_by_id_with_relations(self, application_id: str) -> Optional[Application]:
        stmt = (
            select(Application)
            .where(Application.id == application_id)
            .options(
                selectinload(Application.documents),
                selectinload(Application.quote),
                selectinload(Application.product),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(self, application_number: str) -> Optional[Application]:
        stmt = (
            select(Application)
            .where(Application.application_number == application_number)
            .options(
                selectinload(Application.documents),
                selectinload(Application.quote),
                selectinload(Application.product),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_quote_id(self, quote_id: str) -> Optional[Application]:
        stmt = (
            select(Application)
            .where(Application.quote_id == quote_id)
            .options(
                selectinload(Application.documents),
                selectinload(Application.quote),
                selectinload(Application.product),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_customer(self, customer_id: str) -> Sequence[Application]:
        stmt = (
            select(Application)
            .where(Application.customer_id == customer_id)
            .options(
                selectinload(Application.documents),
                selectinload(Application.quote),
                selectinload(Application.product),
            )
            .order_by(Application.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Application]:
        stmt = (
            select(Application)
            .options(
                selectinload(Application.documents),
                selectinload(Application.quote),
                selectinload(Application.product),
                selectinload(Application.customer),
            )
            .order_by(Application.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if status:
            stmt = stmt.where(Application.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()
