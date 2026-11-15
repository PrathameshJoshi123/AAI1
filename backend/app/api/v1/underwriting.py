"""Underwriting Cases, Triage Queues, Reviews, and Case Notes Endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agents.definitions.underwriting_escalation_agent import (
    UnderwritingEscalationAgent,
    UnderwritingEscalationInput,
)
from app.api.deps import get_db, require_roles
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.auth import User
from app.schemas.common import APIResponse
from app.schemas.underwriting import (
    CaseNoteCreate,
    CaseNoteRead,
    UnderwritingCaseDetailRead,
    UnderwritingCaseRead,
    UnderwritingCaseSummaryRead,
    UnderwritingReviewCreate,
    UnderwritingReviewRead,
)
from app.services.underwriting_service import UnderwritingService

router = APIRouter(prefix="/underwriting", tags=["Underwriting & Reviews"])


@router.get("/triage", response_model=APIResponse[List[UnderwritingCaseSummaryRead]])
async def get_triage_queue(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    risk_rating: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve triage cases with SLA countdowns and risk tiers."""
    svc = UnderwritingService(session)
    cases = await svc.list_triage_cases(
        current_user=current_user,
        status=status,
        priority=priority,
        risk_rating=risk_rating,
        limit=limit,
        offset=offset,
    )
    return APIResponse(data=cases)


@router.get("/cases", response_model=APIResponse[List[UnderwritingCaseRead]])
async def list_cases(
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Legacy compatibility endpoint for listing underwriting cases."""
    svc = UnderwritingService(session)
    summaries = await svc.list_triage_cases(current_user=current_user)
    # Convert to UnderwritingCaseRead for backward compatibility
    case_reads = [
        UnderwritingCaseRead(
            id=s.id,
            case_number=s.case_number,
            application_id=s.application_id,
            customer_id=s.customer_id,
            priority=s.priority,
            risk_rating=s.risk_rating,
            status=s.status,
            sla_deadline=s.sla_deadline,
            created_at=s.created_at,
        )
        for s in summaries
    ]
    return APIResponse(data=case_reads)


@router.get("/cases/{case_number}", response_model=APIResponse[UnderwritingCaseDetailRead])
async def get_case_detail_360(
    case_number: str,
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve full 360-degree customer case dossier including proposal snapshot, KYC documents, reviews, and notes."""
    svc = UnderwritingService(session)
    detail = await svc.get_case_detail_360(case_number, current_user)
    return APIResponse(data=detail)


@router.post("/cases/{case_number}/reviews", response_model=APIResponse[UnderwritingReviewRead], status_code=status.HTTP_201_CREATED)
async def submit_case_review(
    case_number: str,
    data: UnderwritingReviewCreate,
    current_user: User = Depends(require_roles(["Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Submit a formal underwriting review decision with optional loading percentage and conditions."""
    svc = UnderwritingService(session)
    review = await svc.submit_formal_review(case_number, data, current_user)
    return APIResponse(
        data=review,
        message="Review recorded and case status updated successfully.",
    )


@router.post("/cases/{case_number}/ai-escalation", response_model=APIResponse[dict])
async def trigger_ai_escalation(
    case_number: str,
    current_user: User = Depends(require_roles(["Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Trigger the advisory Underwriting Escalation AI Agent to synthesize risk flags and check underwriting tables."""
    svc = UnderwritingService(session)
    case_detail = await svc.get_case_detail_360(case_number, current_user)

    agent = UnderwritingEscalationAgent()
    # Compute age if dob is available
    age = 35
    if case_detail.customer_dob:
        try:
            from datetime import date
            dob = date.fromisoformat(case_detail.customer_dob)
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception:
            pass

    # Extract proposal declarations if present
    p_data = case_detail.proposal_data or {}
    meds = p_data.get("medical_declarations") or {}
    ann_income = float(p_data.get("annual_income") or 500000.0)
    tobacco = bool(p_data.get("tobacco_user", False))

    agent_input = UnderwritingEscalationInput(
        case_number=case_number,
        customer_age=age,
        annual_income=ann_income,
        sum_assured=case_detail.sum_assured,
        tobacco_user=tobacco,
        medical_declarations=meds,
        existing_coverage_amount=float(p_data.get("existing_coverage_amount", 0.0)),
        document_count=len(case_detail.documents),
    )

    agent_output = await agent.run(agent_input, context={"user_id": current_user.id})

    # Persist the risk flags to the case in database
    case = await svc.repo.get_by_case_number(case_number)
    if case:
        case.risk_flags_json = [f.model_dump() for f in agent_output.risk_flags]
        case.medical_risk_summary = agent_output.medical_risk_assessment
        case.financial_risk_summary = agent_output.financial_risk_assessment
        if agent_output.recommended_priority:
            case.priority = agent_output.recommended_priority
        await session.commit()

    return APIResponse(
        data=agent_output.model_dump(),
        message="AI risk escalation synthesis completed. Output is advisory.",
    )


@router.get("/cases/{case_id}/notes", response_model=APIResponse[List[CaseNoteRead]])
async def list_case_notes(
    case_id: str,
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve internal collaboration notes for a case."""
    user_roles = [r.name for r in current_user.roles]
    include_confidential = any(r in ("Underwriter", "Admin", "Owner") for r in user_roles)
    notes_repo = svc_repo = UnderwritingService(session).notes_repo
    notes = await notes_repo.list_for_case(case_id, include_confidential=include_confidential)
    dtos = [
        CaseNoteRead(
            id=n.id,
            case_id=n.case_id,
            author_id=n.author_id,
            author_name=n.author.full_name if n.author else "Staff Member",
            author_role=n.author.roles[0].name if n.author and n.author.roles else "Staff",
            note_type=n.note_type,
            content=n.content,
            is_confidential=n.is_confidential,
            created_at=n.created_at,
        )
        for n in notes
    ]
    return APIResponse(data=dtos)


@router.post("/cases/{case_id}/notes", response_model=APIResponse[CaseNoteRead], status_code=status.HTTP_201_CREATED)
async def add_case_note(
    case_id: str,
    data: CaseNoteCreate,
    current_user: User = Depends(require_roles(["Advisor", "Underwriter", "Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Add an internal discussion note to an underwriting case."""
    svc = UnderwritingService(session)
    note = await svc.add_case_note(case_id, data, current_user)
    return APIResponse(
        data=note,
        message="Note added to case successfully.",
    )
