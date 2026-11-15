"""Customer Email Provisioning and Notification Preferences API Router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_customer, get_current_user, get_db
from app.models.auth import User
from app.models.profile import Customer
from app.schemas.common import APIResponse
from app.schemas.email import (
    UpdateCustomerEmailRequest,
    UserEmailPreferenceRead,
    UserEmailPreferenceUpdate,
)
from app.services.email_service import EmailNotificationService

router = APIRouter(prefix="/customer/email", tags=["Customer Email Management"])


@router.post("/update", response_model=APIResponse[dict])
async def update_customer_email(
    payload: UpdateCustomerEmailRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Explicitly provision / update user's primary email address for notifications."""
    service = EmailNotificationService(session)
    try:
        updated_user = await service.update_user_email(current_user.id, payload.email)
        return APIResponse(
            success=True,
            data={"email": updated_user.email, "user_id": updated_user.id},
            message=f"Notification email successfully updated to '{payload.email}'.",
        )
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )


@router.get("/preferences", response_model=APIResponse[UserEmailPreferenceRead])
async def get_email_preferences(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve granular email notification preferences and consent for current customer."""
    service = EmailNotificationService(session)
    pref = await service.get_or_create_user_preference(current_user.id)
    return APIResponse(
        success=True,
        data=UserEmailPreferenceRead.model_validate(pref),
        message="Email preferences retrieved successfully.",
    )


@router.put("/preferences", response_model=APIResponse[UserEmailPreferenceRead])
async def update_email_preferences(
    payload: UserEmailPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Update granular email notification categories and DPDP consent."""
    service = EmailNotificationService(session)
    updated_pref = await service.update_user_preference(current_user.id, payload)
    return APIResponse(
        success=True,
        data=updated_pref,
        message="Email notification preferences updated successfully.",
    )

