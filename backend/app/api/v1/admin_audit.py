"""Admin Compliance & Audit Vault API Router."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import AuditLogSearchResponse
from app.services.audit_search_service import AuditSearchService

router = APIRouter(prefix="/admin/audit", tags=["Admin - Compliance & Audit"])


@router.get("/search", response_model=AuditLogSearchResponse)
async def search_audit_logs(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    resource_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(25, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> AuditLogSearchResponse:
    """Multi-parameter search across immutable compliance audit trails."""
    service = AuditSearchService(session)
    return await service.search_audit_records(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        size=size,
    )


@router.get("/export")
async def export_audit_csv(
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
):
    """Export compliance records as streaming CSV data."""
    service = AuditSearchService(session)
    csv_data = await service.export_audit_csv(
        action=action,
        resource_type=resource_type,
        from_date=from_date,
        to_date=to_date,
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="ps21_compliance_audit.csv"'},
    )

