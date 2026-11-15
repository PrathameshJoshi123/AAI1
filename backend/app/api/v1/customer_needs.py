"""Customer Needs Assessment Endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_customer, get_db
from app.models.profile import Customer
from app.models.product import InsuranceProduct
from app.models.recommendation import CustomerQualification
from app.schemas.common import APIResponse
from app.schemas.needs_assessment import (
    NeedsAssessmentSubmit,
    NeedsAssessmentResponse,
)
from app.services.needs_assessment_service import NeedsAssessmentService

router = APIRouter(prefix="/customer/needs", tags=["Customer Needs Assessment"])


@router.post("/assess", response_model=APIResponse[NeedsAssessmentResponse])
async def submit_needs_assessment(
    payload: NeedsAssessmentSubmit,
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    result = await NeedsAssessmentService.process_needs_assessment(
        session, customer, payload
    )
    return APIResponse(data=result, message="Needs assessment processed and qualifications saved.")


@router.get("/summary", response_model=APIResponse[dict])
async def get_needs_summary(
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    stmt = (
        select(CustomerQualification)
        .where(CustomerQualification.customer_id == customer.id)
        .order_by(CustomerQualification.created_at.desc())
    )
    res = await session.execute(stmt)
    latest = res.scalars().first()

    qualifying_count = 0
    if latest:
        p_stmt = select(InsuranceProduct).where(
            InsuranceProduct.is_active.is_(True),
            InsuranceProduct.category == latest.target_category,
        )
        p_res = await session.execute(p_stmt)
        qualifying_count = len(p_res.scalars().all())

    observations = []
    if latest and latest.factors_json:
        observations = latest.factors_json.get("key_observations", [])
    if not observations and latest:
        if latest.dependents_count > 0:
            observations.append(f"Financial protection recommended for {latest.dependents_count} dependent family member(s).")
        if latest.has_pre_existing_conditions:
            observations.append("Pre-existing conditions noted; waiting periods apply.")
        if latest.factors_json and latest.factors_json.get("existing_life_cover", 0) > 0:
            observations.append(f"Existing life protection of ₹{latest.factors_json.get('existing_life_cover'):,.0f} factored into gap analysis.")
        if not observations:
            observations.append("Profile indicates optimal eligibility for comprehensive coverage.")

    gap = 0.0
    if latest and latest.factors_json:
        gap = float(latest.factors_json.get("calculated_gap", 0.0))

    data = {
        "has_assessment": latest is not None,
        "qualification_id": latest.id if latest else None,
        "customer_id": latest.customer_id if latest else customer.id,
        "target_category": latest.target_category if latest else None,
        "category": latest.target_category if latest else "term_life",
        "eligibility_status": latest.eligibility_status if latest else None,
        "recommended_sum_assured": float(latest.recommended_sum_assured) if latest and latest.recommended_sum_assured else None,
        "health_risk_tier": latest.health_tier if latest else "standard",
        "health_tier": latest.health_tier if latest else None,
        "calculated_coverage_gap": gap,
        "qualifying_products_count": qualifying_count,
        "key_observations": observations,
        "factors": latest.factors_json if latest else {},
        "created_at": latest.created_at.isoformat() if latest and latest.created_at else None,
    }
    return APIResponse(data=data, message="Latest qualification summary retrieved.")

