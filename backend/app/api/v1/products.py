"""Insurance Products Catalog Endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_roles
from app.core.exceptions import EntityNotFoundException
from app.models.auth import User
from app.models.product import InsuranceProduct
from app.repositories.product_repository import ProductRepository
from app.schemas.common import APIResponse
from app.schemas.product import InsuranceProductRead, ProductCreate

router = APIRouter(prefix="/products", tags=["Insurance Products"])


@router.get("", response_model=APIResponse[List[InsuranceProductRead]])
async def list_products(
    category: Optional[str] = Query(None, description="Optional category filter (term_life, health, motor)"),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve all active insurance products with their configured tiers and underwriting rules."""
    repo = ProductRepository(session)
    products = await repo.list_active_products(category=category)
    return APIResponse(
        data=[InsuranceProductRead.model_validate(p) for p in products]
    )


@router.get("/{product_id}", response_model=APIResponse[InsuranceProductRead])
async def get_product(product_id: str, session: AsyncSession = Depends(get_db)):
    """Retrieve a specific product by its ID with full metadata."""
    repo = ProductRepository(session)
    product = await repo.get_by_id_with_details(product_id)
    if not product:
        product = await repo.get_by_code(product_id)
    if not product:
        raise EntityNotFoundException(f"Insurance product '{product_id}' not found.")
    return APIResponse(
        data=InsuranceProductRead.model_validate(product)
    )


@router.post("", response_model=APIResponse[InsuranceProductRead], status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Create a new insurance product with underwriting metadata (Restricted to Admin / Owner)."""
    repo = ProductRepository(session)
    product = InsuranceProduct(
        code=data.code,
        name=data.name,
        category=data.category,
        description=data.description,
        is_active=data.is_active,
        insurer_name=data.insurer_name,
        insurer_code=data.insurer_code,
        insurer_solvency_ratio=data.insurer_solvency_ratio,
        policy_type=data.policy_type,
        base_rules_json=data.base_rules_json,
        coverage_summary_json=data.coverage_summary_json,
        benefits_list_json=data.benefits_list_json,
        exclusions_list_json=data.exclusions_list_json,
        waiting_periods_json=data.waiting_periods_json,
        required_declarations_json=data.required_declarations_json,
        required_documents_json=data.required_documents_json,
    )
    created = await repo.create(product)
    return APIResponse(
        data=InsuranceProductRead.model_validate(created),
        message="Product created successfully.",
    )
