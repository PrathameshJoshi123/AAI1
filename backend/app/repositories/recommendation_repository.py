"""Repository for Recommendations."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.recommendation import Recommendation
from app.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    def __init__(self, session: AsyncSession):
        super().__init__(Recommendation, session)

    async def list_for_customer(self, customer_id: str) -> Sequence[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(
                Recommendation.customer_id == customer_id,
                Recommendation.status == "active",
            )
            .options(
                selectinload(Recommendation.recommended_product),
                selectinload(Recommendation.configuration),
            )
            .order_by(Recommendation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        all_recs = result.scalars().all()
        # Deduplicate by recommended_product_id, keeping the newest active recommendation
        seen_products = set()
        deduped = []
        for r in all_recs:
            if r.recommended_product_id not in seen_products:
                seen_products.add(r.recommended_product_id)
                deduped.append(r)
        deduped.sort(key=lambda x: float(x.match_score), reverse=True)
        return deduped

    async def get_by_id_with_details(self, rec_id: str) -> Optional[Recommendation]:
        stmt = (
            select(Recommendation)
            .where(Recommendation.id == rec_id)
            .options(
                selectinload(Recommendation.recommended_product),
                selectinload(Recommendation.configuration),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

