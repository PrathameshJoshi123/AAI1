"""Customer Policy Recommendations Endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, get_scoped_customer_id, get_current_customer
from app.ai.agents.definitions.recommendation_agent import RecommendationAgent, RecommendationAgentInput, RecommendationAgentOutput
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.auth import User
from app.repositories.recommendation_repository import RecommendationRepository
from app.schemas.common import APIResponse
from app.schemas.recommendation import RecommendationCreate, RecommendationEvaluateResponse, RecommendationRead
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("", response_model=APIResponse[RecommendationEvaluateResponse])
async def get_recommendations(
    category: Optional[str] = Query(None, description="Optional target category filter"),
    amount: Optional[float] = Query(None, description="Optional sum assured amount requested from HLV calculator"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Fetch active recommendations or dynamically evaluate them for the customer."""
    customer = current_user.customer
    if not customer:
        customer = await get_current_customer(current_user, session)

    service = RecommendationService(session)
    response_data = await service.get_or_evaluate_recommendations(
        customer_id=customer.id,
        target_category=category,
        requested_amount=amount,
        force_recalculate=bool(amount),
    )
    return APIResponse(
        data=response_data,
        message="Policy recommendations retrieved successfully.",
    )


@router.post("/evaluate", response_model=APIResponse[RecommendationEvaluateResponse])
async def evaluate_recommendations(
    data: Optional[RecommendationCreate] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Force re-evaluation of product recommendations based on updated customer qualifications."""
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles or not any(r in ("Admin", "Owner", "Underwriter") for r in user_roles):
        customer = current_user.customer
        if not customer:
            customer = await get_current_customer(current_user, session)
        customer_id = customer.id
    else:
        if not data or not data.customer_id:
            customer = current_user.customer or await get_current_customer(current_user, session)
            customer_id = customer.id
        else:
            customer_id = await get_scoped_customer_id(data.customer_id, current_user)

    target_category = data.target_category if data else None
    requested_amount = data.recommended_sum_assured if data else None
    service = RecommendationService(session)
    response_data = await service.get_or_evaluate_recommendations(
        customer_id=customer_id,
        target_category=target_category,
        requested_amount=requested_amount,
        force_recalculate=True,
    )
    return APIResponse(
        data=response_data,
        message="Product recommendations re-evaluated successfully.",
    )


@router.get("/{rec_id}/explain", response_model=APIResponse[RecommendationAgentOutput])
async def explain_recommendation(
    rec_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Generate explainable, empathetic customer advisory text via Mistral RecommendationAgent."""
    repo = RecommendationRepository(session)
    rec = await repo.get_by_id_with_details(rec_id)
    if not rec:
        raise EntityNotFoundException("Recommendation not found.")

    await get_scoped_customer_id(rec.customer_id, current_user)

    prod = rec.recommended_product
    agent = RecommendationAgent()
    agent_input = RecommendationAgentInput(
        product_name=prod.name,
        product_category=prod.category,
        match_score=float(rec.match_score),
        recommended_sum_assured=float(rec.recommended_sum_assured),
        recommended_term_years=rec.recommended_term_years,
        match_factors=rec.match_factors_json or {},
        exclusions=prod.exclusions_list_json or [],
        customer_age=30,
        dependents_count=1,
    )
    explanation = await agent.run(agent_input, context={})

    return APIResponse(
        data=explanation,
        message="Explainable recommendation rationale generated successfully.",
    )

