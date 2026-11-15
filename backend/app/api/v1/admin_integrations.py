"""Admin Integration Management API Router."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.config import settings
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import IntegrationHealthResponse
from app.schemas.common import APIResponse
from app.schemas.email import (
    EmailDeliveryResult,
    PaginatedEmailLogsResponse,
    SendTestEmailRequest,
)
from app.services.email_service import EmailNotificationService
from app.services.integration_health_service import IntegrationHealthService

router = APIRouter(prefix="/admin/integrations", tags=["Admin - Integrations"])


@router.get("/health", response_model=IntegrationHealthResponse)
async def check_integration_health(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> IntegrationHealthResponse:
    """Retrieve live configuration status and health probes for all external integrations."""
    service = IntegrationHealthService(session)
    return await service.check_all_integrations()


@router.post("/email/test", response_model=APIResponse[EmailDeliveryResult])
async def send_admin_test_email(
    payload: SendTestEmailRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
):
    """Execute live SMTP connectivity and dispatch a diagnostic test email."""
    email_service = EmailNotificationService(session)
    result = await email_service.send_email(
        to_email=str(payload.recipient_email),
        subject="[PS-21] SMTP Notification Engine Live Probe",
        template_name="test_notification",
        context={
            "recipient_email": str(payload.recipient_email),
            "smtp_host": getattr(settings, "SMTP_HOST", "unconfigured"),
            "smtp_port": getattr(settings, "SMTP_PORT", 587),
            "timestamp": str(session.bind.url if hasattr(session, "bind") else "UTC"),
        },
        user_id=current_user.id,
        category="system",
    )
    return APIResponse(
        success=result.success,
        data=result,
        message=result.message,
    )


@router.get("/email/logs", response_model=APIResponse[PaginatedEmailLogsResponse])
async def list_email_delivery_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
):
    """Retrieve filterable, paginated audit records from email_delivery_logs."""
    email_service = EmailNotificationService(session)
    logs_page = await email_service.list_delivery_logs(
        page=page, page_size=page_size, status=status, search=search
    )
    return APIResponse(
        success=True,
        data=logs_page,
        message="Email delivery logs retrieved successfully.",
    )


@router.post("/{service_key}/test")
async def test_integration_connectivity(
    service_key: str,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> dict:
    """Execute live connectivity ping test."""
    service = IntegrationHealthService(session)
    all_health = await service.check_all_integrations()
    target = next((item for item in all_health.integrations if item.service_key == service_key), None)
    
    if not target:
        return {"service_key": service_key, "status": "not_found", "message": "Service key not recognized."}

    return {
        "service_key": service_key,
        "name": target.name,
        "status": target.status,
        "details": target.details,
        "endpoint": target.endpoint_or_host,
    }


