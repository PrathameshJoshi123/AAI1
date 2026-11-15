"""FastAPI router for Consent Management (DPDP & IRDAI compliance)."""
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.consent_repository import ConsentRepository
from app.schemas.common import ResponseEnvelope
from app.schemas.consent import (
    ConsentGrantRequest,
    ConsentRecordRead,
    ConsentRevokeRequest,
    ConsentStatusResponse,
)
from app.services.lead_service import LeadService

router = APIRouter(prefix="/consent", tags=["Consent & Compliance"])


@router.post("", response_model=ResponseEnvelope[ConsentRecordRead], status_code=status.HTTP_201_CREATED)
async def grant_consent(
    payload: ConsentGrantRequest,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Explicitly records legal consent grant with IP and version."""
    if not payload.ip_address and request.client:
        payload.ip_address = request.client.host
    service = LeadService(session)
    record = await service.grant_consent(payload)
    return ResponseEnvelope(data=ConsentRecordRead.model_validate(record))


@router.post("/revoke", response_model=ResponseEnvelope[ConsentRecordRead])
async def revoke_consent(
    payload: ConsentRevokeRequest,
    session: AsyncSession = Depends(get_db),
):
    """Explicitly revokes previously granted consent and applies scoring penalty."""
    service = LeadService(session)
    record = await service.revoke_consent(payload)
    if not record:
        from app.core.exceptions import ResourceNotFoundException
        raise ResourceNotFoundException("Active consent record for this type not found.")
    return ResponseEnvelope(data=ConsentRecordRead.model_validate(record))


@router.get("/{prospect_id}", response_model=ResponseEnvelope[ConsentStatusResponse])
async def get_consent_status(
    prospect_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Check active consents and outreach permission under DPDP Act."""
    repo = ConsentRepository(session)
    active = await repo.get_active_consents_for_prospect(prospect_id)
    active_types = [c.consent_type for c in active]
    can_contact = "marketing_contact" in active_types
    return ResponseEnvelope(
        data=ConsentStatusResponse(
            prospect_id=prospect_id,
            can_contact=can_contact,
            active_consents=active_types,
        )
    )

