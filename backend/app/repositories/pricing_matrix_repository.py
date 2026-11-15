"""Repository for Product Pricing Matrices."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pricing_matrix import ProductPricingMatrix
from app.repositories.base import BaseRepository


class PricingMatrixRepository(BaseRepository[ProductPricingMatrix]):
    def __init__(self, session: AsyncSession):
        super().__init__(ProductPricingMatrix, session)

    async def get_active_by_product_id(self, product_id: str) -> Optional[ProductPricingMatrix]:
        stmt = (
            select(ProductPricingMatrix)
            .where(
                ProductPricingMatrix.product_id == product_id,
                ProductPricingMatrix.is_active.is_(True),
            )
            .order_by(ProductPricingMatrix.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_version(self, version: str) -> Optional[ProductPricingMatrix]:
        stmt = select(ProductPricingMatrix).where(ProductPricingMatrix.matrix_version == version)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_product(self, product_id: str) -> Sequence[ProductPricingMatrix]:
        stmt = (
            select(ProductPricingMatrix)
            .where(ProductPricingMatrix.product_id == product_id)
            .order_by(ProductPricingMatrix.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

