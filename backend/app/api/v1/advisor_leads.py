"""FastAPI router for Advisor-Scoped Lead Management and Outreach."""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.exceptions import PermissionDeniedException, ResourceNotFoundException
from app.models.auth import User
from app.repositories.prospect_repository import ProspectRepository
from app.schemas.common import PaginatedResponse, ResponseEnvelope
from app.schemas.prospect import AdvisorOutreachNoteCreate, ProspectRead
from app.services.lead_service import LeadService

router = APIRouter(prefix="/advisor/leads", tags=["Advisor Lead Queue"])


class LeadStatusUpdateRequest(BaseModel):
    status: str = Field(..., pattern=r"^(new|engaged|qualified|converted|dropped)$")


@router.get("", response_model=PaginatedResponse[ProspectRead])
async def list_assigned_leads(
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_roles(["Advisor"])),
    session: AsyncSession = Depends(get_db),
):
    """Returns leads strictly assigned to the currently authenticated advisor."""
    if not current_user.advisor:
        raise PermissionDeniedException("User profile is not configured as an insurance advisor.")

    repo = ProspectRepository(session)
    skip = (page - 1) * page_size
    prospects, total = await repo.get_advisor_leads(
        advisor_id=current_user.advisor.id,
        status_filter=status,
        skip=skip,
        limit=page_size,
    )

    advisor_name = f"{current_user.first_name} {current_user.last_name}".strip()
    items = []
    for p in prospects:
        can_contact = any(
            c.consent_type == "marketing_contact" and c.revoked_at is None
            for c in (p.consents or [])
        )
        latest_sc = None
        if p.lead_scores:
            latest_sc = float(sorted(p.lead_scores, key=lambda s: s.calculated_at, reverse=True)[0].score)

        items.append(
            ProspectRead(
                id=p.id,
                name=p.name,
                email=p.email,
                phone=p.phone,
                status=p.status,
                segment=p.segment,
                source_name=p.source.name if p.source else None,
                target_insurance_type=p.target_insurance_type,
                assigned_advisor_id=p.assigned_advisor_id,
                assigned_advisor_name=advisor_name,
                assigned_at=p.assigned_at,
                latest_score=latest_sc,
                can_contact=can_contact,
                created_at=p.created_at,
                last_activity_at=p.last_activity_at,
            )
        )

    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


@router.post("/{prospect_id}/notes", response_model=ResponseEnvelope[Dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def log_outreach_note(
    prospect_id: str,
    payload: AdvisorOutreachNoteCreate,
    current_user: User = Depends(require_roles(["Advisor"])),
    session: AsyncSession = Depends(get_db),
):
    """Logs advisor phone or email outreach. Strictly enforces active DPDP marketing consent."""
    if not current_user.advisor:
        raise PermissionDeniedException("User profile is not configured as an insurance advisor.")

    service = LeadService(session)
    try:
        follow_up = await service.advisor_log_outreach(
            prospect_id=prospect_id,
            advisor_id=current_user.advisor.id,
            data=payload,
            actor_user_id=current_user.id,
        )
    except ValueError as e:
        raise ResourceNotFoundException(str(e))
    except PermissionError as e:
        # Non-negotiable consent boundary
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    return ResponseEnvelope(
        data={
            "follow_up_id": follow_up.id,
            "status": follow_up.status,
            "notes": follow_up.notes,
            "due_date": follow_up.due_date.isoformat(),
        }
    )


@router.post("/{prospect_id}/status", response_model=ResponseEnvelope[Dict[str, Any]])
async def update_assigned_lead_status(
    prospect_id: str,
    payload: LeadStatusUpdateRequest,
    current_user: User = Depends(require_roles(["Advisor"])),
    session: AsyncSession = Depends(get_db),
):
    """Allows advisor to advance lead qualification status."""
    if not current_user.advisor:
        raise PermissionDeniedException("User profile is not configured as an insurance advisor.")

    repo = ProspectRepository(session)
    prospect = await repo.get_by_id(prospect_id)
    if not prospect:
        raise ResourceNotFoundException("Lead not found.")

    if prospect.assigned_advisor_id != current_user.advisor.id:
        raise PermissionDeniedException("Access denied: You are not assigned to this lead.")

    prospect.status = payload.status
    prospect.last_activity_at = datetime.now()
    await session.flush()

    return ResponseEnvelope(
        data={
            "prospect_id": prospect.id,
            "new_status": prospect.status,
            "updated_at": prospect.last_activity_at.isoformat(),
        }
    )

