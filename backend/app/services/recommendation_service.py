"""Recommendation coordination and persistence service."""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import EntityNotFoundException
from app.models.product import InsuranceProduct
from app.models.recommendation import CustomerQualification, Recommendation
from app.repositories.product_repository import ProductRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.recommendation import RecommendationRead, RecommendationEvaluateResponse
from app.services.product_matching_service import ProductMatchingService


class RecommendationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.product_repo = ProductRepository(session)
        self.rec_repo = RecommendationRepository(session)

    async def get_or_evaluate_recommendations(
        self,
        customer_id: str,
        target_category: Optional[str] = None,
        requested_amount: Optional[float] = None,
        force_recalculate: bool = False,
    ) -> RecommendationEvaluateResponse:
        """Evaluate catalog products against customer qualifications and return ranked recommendations."""
        # 1. Fetch customer qualification
        q_stmt = (
            select(CustomerQualification)
            .where(CustomerQualification.customer_id == customer_id)
            .order_by(CustomerQualification.updated_at.desc())
        )
        q_res = await self.session.execute(q_stmt)
        qualification = q_res.scalar_one_or_none()

        effective_category = target_category or (qualification.target_category if qualification else "term_life")
        recommended_sa = float(requested_amount) if requested_amount and requested_amount > 0 else (
            float(qualification.recommended_sum_assured) if qualification and qualification.recommended_sum_assured else 10000000.0
        )

        # 2. Check existing active recommendations if not forcing recalculation and no specific requested amount
        if not force_recalculate and not requested_amount:
            existing = await self.rec_repo.list_for_customer(customer_id)
            if existing:
                read_items = [self._map_to_read(r) for r in existing]
                return RecommendationEvaluateResponse(
                    recommendations=read_items,
                    primary_recommendation=read_items[0] if read_items else None,
                    target_category=effective_category,
                    recommended_sum_assured=recommended_sa,
                )

        # 3. Fetch active products and supersede existing recommendations
        await self.session.execute(
            update(Recommendation)
            .where(Recommendation.customer_id == customer_id, Recommendation.status == "active")
            .values(status="superseded")
        )

        products = await self.product_repo.list_active_products()
        evaluated_recs: List[Recommendation] = []

        for prod in products:
            match_res = ProductMatchingService.match_product(
                product=prod,
                qualification=qualification,
                target_category=effective_category,
                override_sum_assured=requested_amount,
            )
            if not match_res:
                continue

            rec = Recommendation(
                customer_id=customer_id,
                recommended_product_id=prod.id,
                configuration_id=match_res.configuration.id if match_res.configuration else None,
                match_score=match_res.match_score,
                recommended_sum_assured=match_res.recommended_sum_assured,
                recommended_term_years=match_res.recommended_term_years,
                rationale=match_res.rationale,
                match_factors_json=match_res.match_factors,
                assumptions_json=match_res.assumptions,
                limitations_json=match_res.limitations,
                alternative_options_json=match_res.alternative_options,
                status="active",
            )
            self.session.add(rec)
            evaluated_recs.append(rec)

        await self.session.commit()

        # Re-fetch with loaded relationships for response
        refreshed = await self.rec_repo.list_for_customer(customer_id)
        read_items = [self._map_to_read(r) for r in refreshed]

        return RecommendationEvaluateResponse(
            recommendations=read_items,
            primary_recommendation=read_items[0] if read_items else None,
            target_category=effective_category,
            recommended_sum_assured=recommended_sa,
        )

    def _map_to_read(self, rec: Recommendation) -> RecommendationRead:
        prod = rec.recommended_product
        return RecommendationRead(
            id=rec.id,
            customer_id=rec.customer_id,
            conversation_id=rec.conversation_id,
            recommended_product_id=rec.recommended_product_id,
            configuration_id=rec.configuration_id,
            match_score=float(rec.match_score),
            recommended_sum_assured=float(rec.recommended_sum_assured),
            recommended_term_years=rec.recommended_term_years,
            rationale=rec.rationale,
            match_factors_json=rec.match_factors_json,
            assumptions_json=rec.assumptions_json,
            limitations_json=rec.limitations_json,
            alternative_options_json=rec.alternative_options_json,
            status=rec.status,
            created_at=rec.created_at,
            product_name=prod.name if prod else None,
            product_code=prod.code if prod else None,
            product_category=prod.category if prod else None,
            insurer_name=prod.insurer_name if prod else None,
            insurer_solvency_ratio=float(prod.insurer_solvency_ratio) if prod else None,
        )

