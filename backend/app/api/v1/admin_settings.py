"""Admin Dynamic System Settings API Router."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import SystemSettingResponse, SystemSettingUpdateRequest
from app.services.system_settings_service import SystemSettingsService

router = APIRouter(prefix="/admin/settings", tags=["Admin - System Settings"])


@router.get("", response_model=List[SystemSettingResponse])
async def get_system_settings(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[SystemSettingResponse]:
    """Retrieve all dynamic platform settings."""
    service = SystemSettingsService(session)
    return await service.get_all_settings()


@router.put("/{key}", response_model=SystemSettingResponse)
async def update_system_setting(
    key: str,
    req: SystemSettingUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> SystemSettingResponse:
    """Update a specific platform setting and record an immutable audit entry."""
    service = SystemSettingsService(session)
    return await service.update_setting(key, req, admin_user_id=current_user.id)

