"""Insurance Quotes Endpoints with Actuarial Calculation Engine."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db, get_scoped_customer_id
from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.auth import User
from app.repositories.quote_repository import QuoteRepository
from app.schemas.common import APIResponse
from app.schemas.quote import QuoteCreate, QuoteRead, QuoteRecalculateRequest
from app.services.quote_service import QuoteService

router = APIRouter(prefix="/quotes", tags=["Quotes"])


@router.post("", response_model=APIResponse[QuoteRead], status_code=status.HTTP_201_CREATED)
@router.post("/calculate", response_model=APIResponse[QuoteRead], status_code=status.HTTP_201_CREATED)
async def create_quote(
    data: QuoteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Generate an official deterministic actuarial quote."""
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer:
            raise PermissionDeniedException("User does not have an active customer profile.")
        customer_id = current_user.customer.id
        # Extract demographic parameters from customer profile if available
        customer = current_user.customer
        age = customer.age if hasattr(customer, "age") and customer.age else 30
        gender = customer.gender if hasattr(customer, "gender") and customer.gender else "male"
        is_smoker = customer.is_smoker if hasattr(customer, "is_smoker") else False
    else:
        if not data.customer_id:
            raise PermissionDeniedException("customer_id is required when creating quotes on behalf of a customer.")
        customer_id = await get_scoped_customer_id(data.customer_id, current_user)
        age = 30
        gender = "male"
        is_smoker = False

    service = QuoteService(session)
    quote = await service.calculate_and_create_quote(
        customer_id=customer_id,
        data=data,
        age=age,
        gender=gender,
        is_smoker=is_smoker,
    )
    return APIResponse(
        data=QuoteRead.model_validate(quote),
        message="Deterministic indicative quote calculated and generated successfully.",
    )


@router.post("/{quote_id}/recalculate", response_model=APIResponse[QuoteRead])
async def recalculate_quote(
    quote_id: str,
    data: QuoteRecalculateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Dynamically recalculate an existing quote with updated riders, sum assured, or frequency."""
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer:
            raise PermissionDeniedException("Customer profile required.")
        customer_id = current_user.customer.id
        customer = current_user.customer
        age = customer.age if hasattr(customer, "age") and customer.age else 30
        gender = customer.gender if hasattr(customer, "gender") and customer.gender else "male"
        is_smoker = customer.is_smoker if hasattr(customer, "is_smoker") else False
    else:
        repo = QuoteRepository(session)
        existing = await repo.get_by_id(quote_id)
        if not existing:
            raise EntityNotFoundException("Quote not found.")
        customer_id = await get_scoped_customer_id(existing.customer_id, current_user)
        age = 30
        gender = "male"
        is_smoker = False

    service = QuoteService(session)
    updated = await service.recalculate_quote(
        quote_id=quote_id,
        customer_id=customer_id,
        data=data,
        age=age,
        gender=gender,
        is_smoker=is_smoker,
    )
    return APIResponse(
        data=QuoteRead.model_validate(updated),
        message="Quote recalculated successfully with updated parameters.",
    )


@router.get("", response_model=APIResponse[List[QuoteRead]])
async def list_quotes(
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """List quotes scoped to the authorized customer."""
    user_roles = [r.name for r in current_user.roles]
    if "Customer" in user_roles:
        if not current_user.customer:
            return APIResponse(data=[])
        effective_customer_id = current_user.customer.id
    else:
        if not customer_id:
            raise PermissionDeniedException("customer_id parameter required for administrative lookup.")
        effective_customer_id = await get_scoped_customer_id(customer_id, current_user)

    repo = QuoteRepository(session)
    quotes = await repo.list_for_customer(effective_customer_id)
    return APIResponse(
        data=[QuoteRead.model_validate(q) for q in quotes]
    )


@router.get("/{identifier}", response_model=APIResponse[QuoteRead])
async def get_quote(
    identifier: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve quote details by UUID or quote number with authorization enforcement."""
    repo = QuoteRepository(session)
    quote = await repo.get_by_id_with_details(identifier)
    if not quote:
        quote = await repo.get_by_quote_number(identifier)

    if not quote:
        raise EntityNotFoundException(f"Quote '{identifier}' not found.")

    await get_scoped_customer_id(quote.customer_id, current_user)
    return APIResponse(data=QuoteRead.model_validate(quote))


@router.post("/{identifier}/send-email", response_model=APIResponse[dict])
async def send_quote_email(
    identifier: str,
    payload: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Dispatch quote summary breakdown to the user's verified or entered email."""
    from app.services.email_service import EmailNotificationService

    repo = QuoteRepository(session)
    quote = await repo.get_by_id_with_details(identifier)
    if not quote:
        quote = await repo.get_by_quote_number(identifier)

    if not quote:
        raise EntityNotFoundException(f"Quote '{identifier}' not found.")

    await get_scoped_customer_id(quote.customer_id, current_user)

    # Determine recipient email
    recipient_email = None
    if payload and payload.get("recipient_email"):
        recipient_email = str(payload["recipient_email"]).strip()
    elif current_user and current_user.email:
        recipient_email = current_user.email

    if not recipient_email:
        raise PermissionDeniedException("A valid recipient email must be provided or registered on your profile.")

    # Context values
    cust_name = f"{current_user.first_name} {current_user.last_name}".strip() if current_user else "Customer"
    prod_name = quote.product.name if hasattr(quote, "product") and quote.product else "Comprehensive Insurance Plan"

    def _format_inr(val):
        if val is None:
            return "N/A"
        try:
            return f"₹{float(val):,.2f}"
        except (ValueError, TypeError):
            return str(val)

    coverage_val = getattr(quote, "sum_assured", None) if getattr(quote, "sum_assured", None) is not None else getattr(quote, "coverage_amount", None)
    total_val = getattr(quote, "total_premium", None) if getattr(quote, "total_premium", None) is not None else getattr(quote, "final_premium", None)

    context = {
        "customer_name": cust_name,
        "quote_number": quote.quote_number,
        "product_name": prod_name,
        "coverage_amount": _format_inr(coverage_val),
        "payment_frequency": quote.payment_frequency.capitalize() if getattr(quote, "payment_frequency", None) else "Annual",
        "base_premium": _format_inr(getattr(quote, "base_premium", None)),
        "tax_amount": _format_inr(getattr(quote, "tax_amount", None)),
        "final_premium": _format_inr(total_val),
        "portal_url": f"http://localhost:3000/customer/onboarding/{quote.id}",
    }

    email_service = EmailNotificationService(session)
    result = await email_service.send_email(
        to_email=recipient_email,
        subject=f"[PS-21] Your Official Insurance Quote {quote.quote_number}",
        template_name="quote_summary",
        context=context,
        user_id=current_user.id,
        category="quote",
    )

    return APIResponse(
        success=result.success,
        data={
            "status": result.status,
            "recipient": recipient_email,
            "quote_number": quote.quote_number,
            "delivery_log_id": result.delivery_log_id,
            "details": result.details,
        },
        message=result.message,
    )

