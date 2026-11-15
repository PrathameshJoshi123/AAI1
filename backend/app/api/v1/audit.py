"""Audit Trail Endpoints."""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_roles
from app.models.auth import User
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit import AuditLogRead
from app.schemas.common import APIResponse

router = APIRouter(prefix="/audit", tags=["Audit & Compliance"])


@router.get("", response_model=APIResponse[List[AuditLogRead]])
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve compliance and security audit logs (Admin / Owner only)."""
    repo = AuditRepository(session)
    logs = await repo.list_all(skip=skip, limit=limit)
    return APIResponse(
        data=[AuditLogRead.model_validate(log) for log in logs]
    )

