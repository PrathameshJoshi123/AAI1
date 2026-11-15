"""Repository for Insurance Products, Configurations and Actuarial Matrices."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import InsuranceProduct, ProductConfiguration
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[InsuranceProduct]):
    def __init__(self, session: AsyncSession):
        super().__init__(InsuranceProduct, session)

    async def list_active_products(self, category: Optional[str] = None) -> Sequence[InsuranceProduct]:
        stmt = (
            select(InsuranceProduct)
            .where(InsuranceProduct.is_active.is_(True))
            .options(
                selectinload(InsuranceProduct.configurations),
                selectinload(InsuranceProduct.pricing_matrices),
            )
        )
        if category:
            stmt = stmt.where(InsuranceProduct.category == category)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_code(self, code: str) -> Optional[InsuranceProduct]:
        stmt = (
            select(InsuranceProduct)
            .where(InsuranceProduct.code == code)
            .options(
                selectinload(InsuranceProduct.configurations),
                selectinload(InsuranceProduct.pricing_matrices),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, product_id: str) -> Optional[InsuranceProduct]:
        stmt = (
            select(InsuranceProduct)
            .where(InsuranceProduct.id == product_id)
            .options(
                selectinload(InsuranceProduct.configurations),
                selectinload(InsuranceProduct.pricing_matrices),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
