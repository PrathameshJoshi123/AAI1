"""Customer Journey Progression and Resumption Endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_customer, get_db
from app.models.profile import Customer
from app.schemas.common import APIResponse
from app.schemas.journey import (
    JourneyStatusResponse,
    JourneyTransitionRequest,
    ResumeJourneyResponse,
)
from app.services.customer_journey_service import CustomerJourneyService

router = APIRouter(prefix="/customer/journey", tags=["Customer Journey"])


@router.get("/status", response_model=APIResponse[JourneyStatusResponse])
async def get_journey_status(
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    status_data = await CustomerJourneyService.get_journey_status(session, customer)
    return APIResponse(data=status_data, message="Journey status retrieved successfully.")


@router.post("/transition", response_model=APIResponse[str])
async def transition_journey(
    payload: JourneyTransitionRequest,
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    new_stage = await CustomerJourneyService.transition_stage(
        session, customer, payload.target_stage
    )
    return APIResponse(data=new_stage, message=f"Journey transitioned to '{new_stage}'.")


@router.post("/resume", response_model=APIResponse[ResumeJourneyResponse])
async def resume_journey(
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    resume_data = await CustomerJourneyService.resume_journey(session, customer)
    return APIResponse(data=resume_data, message="Journey state resumed successfully.")

