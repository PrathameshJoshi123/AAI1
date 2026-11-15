"""Insurance Applications Endpoints: Dynamic proposals, multi-step auto-save, and proposal submission."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, get_scoped_customer_id
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.auth import User
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDetailRead,
    ApplicationDraftUpdate,
    ApplicationRead,
    ApplicationSubmitRequest,
    DynamicRequirementsResponse,
)
from app.schemas.common import APIResponse
from app.schemas.document import DocumentRead
from app.services.application_service import ApplicationService
from app.services.dynamic_proposal_service import DynamicProposalService

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.post("/draft", response_model=APIResponse[ApplicationRead], status_code=status.HTTP_201_CREATED)
async def get_or_create_draft(
    data: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve existing proposal draft or initialize a new draft for a converted quote."""
    app_svc = ApplicationService(session)
    application = await app_svc.get_or_create_draft(data.quote_id, current_user)
    return APIResponse(
        data=ApplicationRead.model_validate(application),
        message="Proposal draft loaded.",
    )


@router.put("/{id}/draft", response_model=APIResponse[ApplicationRead])
async def update_draft_step(
    id: str,
    data: ApplicationDraftUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Auto-save step data and update progress in background."""
    app_svc = ApplicationService(session)
    updated = await app_svc.update_draft(id, data, current_user)
    return APIResponse(
        data=ApplicationRead.model_validate(updated),
        message="Step draft auto-saved successfully.",
    )


@router.get("/{id}/requirements", response_model=APIResponse[DynamicRequirementsResponse])
async def get_application_requirements(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Dynamically resolves required declarations and documents checklist for the application's product."""
    repo = ApplicationRepository(session)
    app = await repo.get_by_id_with_relations(id)
    if not app:
        raise EntityNotFoundException("Application not found.")

    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer or current_user.customer.id != app.customer_id:
            raise PermissionDeniedException("Unauthorized to access requirements for this application.")

    reqs = DynamicProposalService.resolve_requirements(app.id, app.product, app.quote)
    return APIResponse(data=reqs)


@router.get("/{id}", response_model=APIResponse[ApplicationDetailRead])
async def get_application_detail(
    id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Get complete proposal details, relations, and uploaded document metadata."""
    repo = ApplicationRepository(session)
    app = await repo.get_by_id_with_relations(id)
    if not app:
        raise EntityNotFoundException("Application not found.")

    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer or current_user.customer.id != app.customer_id:
            raise PermissionDeniedException("Unauthorized to view this application.")

    detail = ApplicationDetailRead(
        id=app.id,
        application_number=app.application_number,
        customer_id=app.customer_id,
        quote_id=app.quote_id,
        product_id=app.product_id,
        status=app.status,
        current_step=app.current_step,
        step_progress_json=app.step_progress_json,
        proposal_data_json=app.proposal_data_json,
        proposal_checksum=app.proposal_checksum,
        submitted_at=app.submitted_at,
        created_at=app.created_at,
        documents=[DocumentRead.model_validate(d) for d in app.documents],
        product_name=app.product.name if app.product else None,
        product_code=app.product.code if app.product else None,
        insurer_name=getattr(app.product, "insurer_name", "Star Union Life & General"),
        quote_number=app.quote.quote_number if app.quote else None,
        sum_assured=float(app.quote.sum_assured) if app.quote and app.quote.sum_assured else None,
        policy_term_years=app.quote.policy_term_years if app.quote else None,
        total_premium=float(app.quote.total_premium) if app.quote and app.quote.total_premium else None,
    )
    return APIResponse(data=detail)


@router.post("/{id}/submit", response_model=APIResponse[ApplicationRead])
async def submit_application_proposal(
    id: str,
    data: ApplicationSubmitRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Formally submits the application proposal, generates SHA-256 checksum, and triggers underwriting."""
    app_svc = ApplicationService(session)
    submitted_app = await app_svc.submit_proposal(id, data, current_user)
    return APIResponse(
        data=ApplicationRead.model_validate(submitted_app),
        message="Proposal successfully submitted. Case forwarded to underwriting review.",
    )


@router.get("", response_model=APIResponse[List[ApplicationRead]])
async def list_applications(
    customer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List applications strictly scoped to the customer, or all for authorized staff."""
    repo = ApplicationRepository(session)
    user_roles = [r.name for r in current_user.roles]

    if "Customer" in user_roles:
        if not current_user.customer:
            return APIResponse(data=[])
        apps = await repo.list_for_customer(current_user.customer.id)
    else:
        # Staff: Advisor, Underwriter, Admin, Owner
        if customer_id:
            effective_customer_id = await get_scoped_customer_id(customer_id, current_user)
            apps = await repo.list_for_customer(effective_customer_id)
        else:
            apps = await repo.list_all(status=status)

    return APIResponse(data=[ApplicationRead.model_validate(a) for a in apps])
