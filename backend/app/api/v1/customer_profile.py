"""Customer Profile Management Endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_customer, get_current_user, get_db
from app.models.auth import User
from app.models.profile import Customer
from app.schemas.common import APIResponse
from app.schemas.customer import CustomerProfileRead, CustomerProfileUpdate

router = APIRouter(prefix="/customer/profile", tags=["Customer Profile"])


@router.get("", response_model=APIResponse[CustomerProfileRead])
async def get_profile(
    current_user: User = Depends(get_current_user),
    customer: Customer = Depends(get_current_customer),
):
    profile = CustomerProfileRead(
        id=customer.id,
        user_id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        date_of_birth=customer.date_of_birth,
        marital_status=customer.marital_status,
        occupation=customer.occupation,
        annual_income=float(customer.annual_income) if customer.annual_income else None,
        health_status=customer.health_status,
        risk_tier=customer.risk_tier,
        preferred_language=customer.preferred_language,
        city=customer.city,
        pincode=customer.pincode,
        state=customer.state,
        gender=customer.gender,
        tobacco_user=customer.tobacco_user,
        onboarding_stage=customer.onboarding_stage,
        active_conversation_id=customer.active_conversation_id,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
    return APIResponse(data=profile, message="Customer profile retrieved successfully.")


@router.put("", response_model=APIResponse[CustomerProfileRead])
async def update_profile(
    payload: CustomerProfileUpdate,
    current_user: User = Depends(get_current_user),
    customer: Customer = Depends(get_current_customer),
    session: AsyncSession = Depends(get_db),
):
    if payload.first_name is not None:
        current_user.first_name = payload.first_name
    if payload.last_name is not None:
        current_user.last_name = payload.last_name
    if payload.phone is not None:
        current_user.phone = payload.phone

    if payload.date_of_birth is not None:
        customer.date_of_birth = payload.date_of_birth
    if payload.marital_status is not None:
        customer.marital_status = payload.marital_status
    if payload.occupation is not None:
        customer.occupation = payload.occupation
    if payload.annual_income is not None:
        customer.annual_income = payload.annual_income
    if payload.gender is not None:
        customer.gender = payload.gender
    if payload.city is not None:
        customer.city = payload.city
    if payload.pincode is not None:
        customer.pincode = payload.pincode
    if payload.state is not None:
        customer.state = payload.state
    if payload.tobacco_user is not None:
        customer.tobacco_user = payload.tobacco_user
    if payload.preferred_language is not None:
        customer.preferred_language = payload.preferred_language

    await session.commit()
    await session.refresh(customer)
    await session.refresh(current_user)

    updated_profile = CustomerProfileRead(
        id=customer.id,
        user_id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone=current_user.phone,
        date_of_birth=customer.date_of_birth,
        marital_status=customer.marital_status,
        occupation=customer.occupation,
        annual_income=float(customer.annual_income) if customer.annual_income else None,
        health_status=customer.health_status,
        risk_tier=customer.risk_tier,
        preferred_language=customer.preferred_language,
        city=customer.city,
        pincode=customer.pincode,
        state=customer.state,
        gender=customer.gender,
        tobacco_user=customer.tobacco_user,
        onboarding_stage=customer.onboarding_stage,
        active_conversation_id=customer.active_conversation_id,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
    return APIResponse(data=updated_profile, message="Customer profile updated successfully.")

