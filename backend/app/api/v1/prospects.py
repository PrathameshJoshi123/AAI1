"""FastAPI router for Prospect Ingestion and Pipeline Management."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.core.exceptions import PermissionDeniedException, ResourceNotFoundException
from app.models.auth import User
from app.repositories.consent_repository import ConsentRepository
from app.repositories.prospect_repository import ProspectRepository
from app.schemas.common import PaginatedResponse, ResponseEnvelope
from app.schemas.prospect import (
    AdvisorAssignRequest,
    LeadScoreRead,
    PipelineKPIsRead,
    ProspectCreate,
    ProspectDetailRead,
    ProspectRead,
    ProspectUpdate,
    ScoreFactorRead,
)
from app.services.lead_assignment_service import LeadAssignmentService
from app.services.lead_scoring_service import LeadScoringService
from app.services.lead_service import LeadService
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/prospects", tags=["Prospects & Leads"])


def _to_prospect_read(prospect, can_contact: bool) -> ProspectRead:
    advisor_name = None
    if prospect.assigned_advisor and prospect.assigned_advisor.user:
        advisor_name = f"{prospect.assigned_advisor.user.first_name} {prospect.assigned_advisor.user.last_name}".strip()

    latest_sc = None
    if prospect.lead_scores:
        latest_sc = float(sorted(prospect.lead_scores, key=lambda s: s.calculated_at, reverse=True)[0].score)

    return ProspectRead(
        id=prospect.id,
        name=prospect.name,
        email=prospect.email,
        phone=prospect.phone,
        status=prospect.status,
        segment=prospect.segment,
        source_name=prospect.source.name if prospect.source else None,
        target_insurance_type=prospect.target_insurance_type,
        assigned_advisor_id=prospect.assigned_advisor_id,
        assigned_advisor_name=advisor_name,
        assigned_at=prospect.assigned_at,
        latest_score=latest_sc,
        can_contact=can_contact,
        created_at=prospect.created_at,
        last_activity_at=prospect.last_activity_at,
    )


@router.post("", response_model=ResponseEnvelope[ProspectRead], status_code=status.HTTP_201_CREATED)
async def ingest_prospect(
    payload: ProspectCreate,
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    """Public ingestion endpoint for visitor registration or lead capture."""
    ip_addr = request.client.host if request.client else None
    service = LeadService(session)
    prospect = await service.ingest_prospect(payload, ip_address=ip_addr)
    can_contact = await service.check_contactability(prospect.id)
    return ResponseEnvelope(data=_to_prospect_read(prospect, can_contact))


@router.get("", response_model=PaginatedResponse[ProspectRead])
async def list_prospects(
    query: Optional[str] = Query(None, description="Search by name, email, phone, ID"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    segment: Optional[List[str]] = Query(None, description="Filter by segment"),
    source_id: Optional[int] = Query(None),
    assigned_advisor_id: Optional[str] = Query(None),
    unassigned_only: bool = Query(False),
    consented_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("last_activity_at"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Admin endpoint to search, filter, and paginate pipeline prospects."""
    repo = ProspectRepository(session)
    consent_repo = ConsentRepository(session)
    skip = (page - 1) * page_size

    prospects, total = await repo.search_and_filter(
        query=query,
        status_filter=status,
        segment_filter=segment,
        source_id=source_id,
        assigned_advisor_id=assigned_advisor_id,
        unassigned_only=unassigned_only,
        consented_only=consented_only,
        skip=skip,
        limit=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    items = []
    for p in prospects:
        can_contact = any(
            c.consent_type == "marketing_contact" and c.revoked_at is None
            for c in (p.consents or [])
        )
        items.append(_to_prospect_read(p, can_contact))

    return PaginatedResponse.create(items=items, total=total, page=page, page_size=page_size)


@router.get("/kpis", response_model=ResponseEnvelope[PipelineKPIsRead])
async def get_pipeline_kpis(
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Returns high-level pipeline funnel KPIs."""
    repo = ProspectRepository(session)
    kpis = await repo.get_pipeline_kpis()
    return ResponseEnvelope(data=PipelineKPIsRead(**kpis))


@router.get("/advisors", response_model=ResponseEnvelope[List[Dict[str, Any]]])
async def get_advisors_workload(
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Returns list of active advisors with real-time caseload metrics."""
    assignment_service = LeadAssignmentService(session)
    advisors = await assignment_service.get_advisors_with_workload()
    return ResponseEnvelope(data=advisors)


@router.get("/{prospect_id}", response_model=ResponseEnvelope[ProspectDetailRead])
async def get_prospect_detail(
    prospect_id: str,
    current_user: User = Depends(require_roles(["Admin", "Owner", "Advisor"])),
    session: AsyncSession = Depends(get_db),
):
    """Fetches full prospect profile, latest score factors, and consents."""
    repo = ProspectRepository(session)
    prospect = await repo.get_detail(prospect_id)
    if not prospect:
        raise ResourceNotFoundException("Prospect not found.")

    # Scoping for advisors
    user_roles = [r.name for r in current_user.roles]
    if "Advisor" in user_roles and "Admin" not in user_roles and "Owner" not in user_roles:
        if not current_user.advisor or prospect.assigned_advisor_id != current_user.advisor.id:
            raise PermissionDeniedException("Access denied: Lead is not assigned to you.")

    # Parse latest score
    latest_score_dto = None
    if prospect.lead_scores:
        sorted_scores = sorted(prospect.lead_scores, key=lambda s: s.calculated_at, reverse=True)
        top_score = sorted_scores[0]
        raw_factors = (top_score.score_factors_json or {}).get("factors", [])
        factors_dto = [
            ScoreFactorRead(
                rule_code=f.get("rule_code", ""),
                rule_name=f.get("rule_name", ""),
                category=f.get("category", ""),
                points_awarded=f.get("points_awarded", 0),
                rationale=f.get("rationale", ""),
            )
            for f in raw_factors
        ]
        latest_score_dto = LeadScoreRead(
            id=top_score.id,
            score=float(top_score.score),
            calculated_at=top_score.calculated_at,
            factors=factors_dto,
        )

    # Active consents
    active_consents = [
        c.consent_type for c in prospect.consents if c.revoked_at is None
    ]
    can_contact = "marketing_contact" in active_consents

    advisor_name = None
    if prospect.assigned_advisor and prospect.assigned_advisor.user:
        advisor_name = f"{prospect.assigned_advisor.user.first_name} {prospect.assigned_advisor.user.last_name}".strip()

    detail = ProspectDetailRead(
        id=prospect.id,
        name=prospect.name,
        email=prospect.email,
        phone=prospect.phone,
        status=prospect.status,
        segment=prospect.segment,
        source_id=prospect.source_id,
        source_name=prospect.source.name if prospect.source else None,
        channel_type=prospect.source.channel_type if prospect.source else None,
        target_insurance_type=prospect.target_insurance_type,
        estimated_budget_min=float(prospect.estimated_budget_min) if prospect.estimated_budget_min else None,
        estimated_budget_max=float(prospect.estimated_budget_max) if prospect.estimated_budget_max else None,
        assigned_advisor_id=prospect.assigned_advisor_id,
        assigned_advisor_name=advisor_name,
        assigned_at=prospect.assigned_at,
        created_at=prospect.created_at,
        last_activity_at=prospect.last_activity_at,
        latest_score=latest_score_dto,
        active_consents=active_consents,
        can_contact=can_contact,
        signals_count=len(prospect.signals),
    )
    return ResponseEnvelope(data=detail)


@router.patch("/{prospect_id}", response_model=ResponseEnvelope[ProspectRead])
async def update_prospect(
    prospect_id: str,
    payload: ProspectUpdate,
    current_user: User = Depends(require_roles(["Admin", "Owner", "Advisor"])),
    session: AsyncSession = Depends(get_db),
):
    """Updates prospect editable attributes."""
    repo = ProspectRepository(session)
    prospect = await repo.get_by_id(prospect_id)
    if not prospect:
        raise ResourceNotFoundException("Prospect not found.")

    user_roles = [r.name for r in current_user.roles]
    if "Advisor" in user_roles and "Admin" not in user_roles and "Owner" not in user_roles:
        if not current_user.advisor or prospect.assigned_advisor_id != current_user.advisor.id:
            raise PermissionDeniedException("Access denied: Lead is not assigned to you.")

    if payload.name is not None:
        prospect.name = payload.name
    if payload.email is not None:
        prospect.email = str(payload.email)
    if payload.phone is not None:
        prospect.phone = payload.phone
    if payload.status is not None:
        prospect.status = payload.status
    if payload.target_insurance_type is not None:
        prospect.target_insurance_type = payload.target_insurance_type
    if payload.estimated_budget_min is not None:
        prospect.estimated_budget_min = payload.estimated_budget_min
    if payload.estimated_budget_max is not None:
        prospect.estimated_budget_max = payload.estimated_budget_max

    prospect.last_activity_at = datetime.now()
    await session.flush()

    # Recalculate score
    scoring_service = LeadScoringService(session)
    await scoring_service.calculate_and_record_score(prospect)

    lead_service = LeadService(session)
    can_contact = await lead_service.check_contactability(prospect.id)
    return ResponseEnvelope(data=_to_prospect_read(prospect, can_contact))


@router.post("/{prospect_id}/assign", response_model=ResponseEnvelope[ProspectRead])
async def assign_advisor(
    prospect_id: str,
    payload: AdvisorAssignRequest,
    request: Request,
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Manually assign or reassign lead to an advisor with audit trail."""
    repo = ProspectRepository(session)
    prospect = await repo.get_by_id(prospect_id)
    if not prospect:
        raise ResourceNotFoundException("Prospect not found.")

    ip_addr = request.client.host if request.client else None
    assignment_service = LeadAssignmentService(session)
    try:
        await assignment_service.manually_assign_lead(
            prospect=prospect,
            advisor_id=payload.advisor_id,
            actor_user_id=current_user.id,
            notes=payload.notes,
            ip_address=ip_addr,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    lead_service = LeadService(session)
    can_contact = await lead_service.check_contactability(prospect.id)
    return ResponseEnvelope(data=_to_prospect_read(prospect, can_contact))


@router.post("/{prospect_id}/recalculate-score", response_model=ResponseEnvelope[LeadScoreRead])
async def recalculate_score(
    prospect_id: str,
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Forces on-demand deterministic score re-evaluation."""
    repo = ProspectRepository(session)
    prospect = await repo.get_by_id(prospect_id)
    if not prospect:
        raise ResourceNotFoundException("Prospect not found.")

    scoring_service = LeadScoringService(session)
    sc = await scoring_service.calculate_and_record_score(prospect)

    factors_dto = [
        ScoreFactorRead(
            rule_code=f.get("rule_code", ""),
            rule_name=f.get("rule_name", ""),
            category=f.get("category", ""),
            points_awarded=f.get("points_awarded", 0),
            rationale=f.get("rationale", ""),
        )
        for f in (sc.score_factors_json or {}).get("factors", [])
    ]
    return ResponseEnvelope(
        data=LeadScoreRead(
            id=sc.id,
            score=float(sc.score),
            calculated_at=sc.calculated_at,
            factors=factors_dto,
        )
    )


@router.get("/{prospect_id}/timeline", response_model=ResponseEnvelope[List[Dict[str, Any]]])
async def get_lead_timeline(
    prospect_id: str,
    current_user: User = Depends(require_roles(["Admin", "Owner", "Advisor"])),
    session: AsyncSession = Depends(get_db),
):
    """Returns chronological aggregated activity timeline for the lead."""
    repo = ProspectRepository(session)
    prospect = await repo.get_by_id(prospect_id)
    if not prospect:
        raise ResourceNotFoundException("Prospect not found.")

    user_roles = [r.name for r in current_user.roles]
    if "Advisor" in user_roles and "Admin" not in user_roles and "Owner" not in user_roles:
        if not current_user.advisor or prospect.assigned_advisor_id != current_user.advisor.id:
            raise PermissionDeniedException("Access denied: Lead is not assigned to you.")

    timeline_service = TimelineService(session)
    events = await timeline_service.get_lead_timeline(prospect_id)
    return ResponseEnvelope(data=events)

