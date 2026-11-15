"""Needs Assessment and Customer Qualification Service."""
from datetime import datetime, timezone
from typing import Any, Dict, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Customer
from app.models.product import InsuranceProduct
from app.models.recommendation import CustomerQualification
from app.schemas.needs_assessment import NeedsAssessmentSubmit, NeedsAssessmentResponse


class NeedsAssessmentService:
    @staticmethod
    async def process_needs_assessment(
        session: AsyncSession,
        customer: Customer,
        data: NeedsAssessmentSubmit,
    ) -> NeedsAssessmentResponse:
        # 1. Deterministic health risk tiering
        if data.has_pre_existing_conditions and data.tobacco_user:
            health_tier = "rated"
        elif data.has_pre_existing_conditions or data.tobacco_user:
            health_tier = "standard"
        elif data.age < 35:
            health_tier = "preferred_plus"
        else:
            health_tier = "standard"

        # 2. Coverage calculation
        if data.category == "term_life":
            # Rule of thumb: 10x - 15x annual income depending on dependents
            multiplier = 15 if data.dependents_count >= 2 else (12 if data.dependents_count == 1 else 10)
            target_cover = data.annual_income * multiplier
            coverage_gap = max(0.0, target_cover - data.existing_life_cover)
            recommended_cover = round(coverage_gap / 500000.0) * 500000.0 if coverage_gap > 0 else 2500000.0
            if data.desired_coverage_amount and data.desired_coverage_amount > recommended_cover:
                recommended_cover = data.desired_coverage_amount
        elif data.category == "health":
            # Benchmark family health cover: Base 5L + 5L per dependent
            target_cover = 500000.0 + (data.dependents_count * 500000.0)
            coverage_gap = max(0.0, target_cover - data.existing_health_cover)
            recommended_cover = max(500000.0, coverage_gap)
        else:
            coverage_gap = 0.0
            recommended_cover = 500000.0

        # 3. Generate key observations
        observations: List[str] = []
        if data.dependents_count > 0:
            observations.append(f"Financial protection recommended for {data.dependents_count} dependent family member(s).")
        if data.tobacco_user:
            observations.append("Declared tobacco usage requires standard non-preferred premium tier.")
        if data.has_pre_existing_conditions:
            observations.append("Pre-existing conditions noted; waiting periods or medical questionnaire will apply.")
        if data.existing_life_cover > 0:
            observations.append(f"Existing life protection of ₹{data.existing_life_cover:,.0f} factored into gap analysis.")
        if not observations:
            observations.append("Profile indicates optimal eligibility for comprehensive coverage.")

        # 4. Count qualifying products from database
        stmt = (
            select(InsuranceProduct)
            .where(
                InsuranceProduct.is_active.is_(True),
                InsuranceProduct.category == data.category,
            )
        )
        res = await session.execute(stmt)
        matching_products = res.scalars().all()
        qualifying_count = len(matching_products)

        # 5. Persist or update CustomerQualification
        qual_stmt = (
            select(CustomerQualification)
            .where(
                CustomerQualification.customer_id == customer.id,
                CustomerQualification.target_category == data.category,
            )
            .order_by(CustomerQualification.created_at.desc())
        )
        q_res = await session.execute(qual_stmt)
        qualification = q_res.scalars().first()

        factors: Dict[str, Any] = {
            "declared_annual_income": data.annual_income,
            "dependents": data.dependents_count,
            "marital_status": data.marital_status,
            "occupation": data.occupation,
            "tobacco_user": data.tobacco_user,
            "has_pre_existing_conditions": data.has_pre_existing_conditions,
            "pre_existing_details": data.pre_existing_conditions_details,
            "existing_life_cover": data.existing_life_cover,
            "existing_health_cover": data.existing_health_cover,
            "calculated_gap": coverage_gap,
            "desired_coverage_amount": data.desired_coverage_amount,
            "age": data.age,
            "key_observations": observations,
        }

        now_utc = datetime.now(timezone.utc)
        if not qualification:
            qualification = CustomerQualification(
                customer_id=customer.id,
                target_category=data.category,
                eligibility_status="eligible",
                financial_capacity=data.annual_income,
                health_tier=health_tier,
                age=data.age,
                dependents_count=data.dependents_count,
                has_pre_existing_conditions=data.has_pre_existing_conditions,
                existing_coverage_amount=data.existing_life_cover if data.category == "term_life" else data.existing_health_cover,
                recommended_sum_assured=recommended_cover,
                factors_json=factors,
                completed_steps_json=["demographics", "financials", "health", "portfolio"],
            )
            session.add(qualification)
        else:
            qualification.eligibility_status = "eligible"
            qualification.financial_capacity = data.annual_income
            qualification.health_tier = health_tier
            qualification.age = data.age
            qualification.dependents_count = data.dependents_count
            qualification.has_pre_existing_conditions = data.has_pre_existing_conditions
            qualification.existing_coverage_amount = data.existing_life_cover if data.category == "term_life" else data.existing_health_cover
            qualification.recommended_sum_assured = recommended_cover
            qualification.factors_json = factors
            qualification.completed_steps_json = ["demographics", "financials", "health", "portfolio"]

        # Also update customer profile details
        customer.occupation = data.occupation
        customer.annual_income = data.annual_income
        customer.marital_status = data.marital_status
        customer.tobacco_user = data.tobacco_user
        customer.onboarding_stage = "product_matching"

        await session.commit()
        await session.refresh(qualification)

        return NeedsAssessmentResponse(
            qualification_id=qualification.id,
            customer_id=customer.id,
            category=data.category,
            eligibility_status=qualification.eligibility_status,
            calculated_coverage_gap=coverage_gap,
            recommended_sum_assured=recommended_cover,
            health_risk_tier=health_tier,
            key_observations=observations,
            qualifying_products_count=qualifying_count,
            factors=factors,
            created_at=qualification.created_at,
        )

