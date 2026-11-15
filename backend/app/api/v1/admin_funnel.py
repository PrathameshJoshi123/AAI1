"""Admin Conversion Funnel API Router."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import ConversionFunnelResponse
from app.services.conversion_funnel_service import ConversionFunnelService

router = APIRouter(prefix="/admin/funnel", tags=["Admin - Conversion Funnel"])


@router.get("", response_model=ConversionFunnelResponse)
async def get_conversion_funnel(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> ConversionFunnelResponse:
    """Retrieve 8-stage conversion funnel and leakage point analysis."""
    service = ConversionFunnelService(session)
    return await service.get_funnel_metrics()

