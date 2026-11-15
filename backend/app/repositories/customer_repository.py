"""Customer Data Access Repository."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Customer, session)

    async def get_by_user_id(self, user_id: str) -> Optional[Customer]:
        stmt = select(Customer).where(Customer.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

