"""Admin Product Catalog Management API Router."""
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.base import utc_now
from app.models.auth import User
from app.models.product import InsuranceProduct, ProductConfiguration
from app.models.pricing_matrix import ProductPricingMatrix
from app.models.audit import AuditLog
from app.schemas.admin import (
    AdminProductCreateRequest,
    AdminProductUpdateRequest,
    AdminProductResponse,
)

router = APIRouter(prefix="/admin/products", tags=["Admin - Products"])


@router.get("", response_model=List[AdminProductResponse])
async def list_admin_products(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[AdminProductResponse]:
    """List all products in the catalog including inactive ones."""
    query = (
        select(InsuranceProduct)
        .options(selectinload(InsuranceProduct.configurations))
        .order_by(InsuranceProduct.created_at.desc())
    )
    result = await session.execute(query)
    products = result.scalars().all()

    responses: List[AdminProductResponse] = []
    for p in products:
        min_sa = 1000000.0
        max_sa = 10000000.0
        if p.configurations:
            min_sa = float(p.configurations[0].min_sum_assured)
            max_sa = float(p.configurations[0].max_sum_assured)

        responses.append(
            AdminProductResponse(
                id=p.id,
                name=p.name,
                category=p.category,
                description=p.description,
                base_premium=450.0,
                min_sum_assured=min_sa,
                max_sum_assured=max_sa,
                min_age=18,
                max_age=65,
                is_active=p.is_active,
                coverage_details=p.base_rules_json or {},
                benefits_list=[b.get("title", "") for b in (p.benefits_list_json or []) if isinstance(b, dict)],
                exclusions_list=[e.get("title", "") for e in (p.exclusions_list_json or []) if isinstance(e, dict)],
                required_declarations=[d.get("title", "") for d in (p.required_declarations_json or []) if isinstance(d, dict)],
                required_documents=[doc.get("title", "") for doc in (p.required_documents_json or []) if isinstance(doc, dict)],
                created_at=p.created_at,
                updated_at=p.updated_at,
            )
        )
    return responses


@router.post("", response_model=AdminProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    req: AdminProductCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> AdminProductResponse:
    """Create a new insurance product with configuration tier and pricing matrix."""
    prod_code = f"{req.category.upper()[:4]}-{uuid.uuid4().hex[:6].upper()}"
    new_product = InsuranceProduct(
        code=prod_code,
        name=req.name,
        category=req.category,
        description=req.description or f"{req.name} comprehensive protection policy",
        is_active=req.is_active,
        base_rules_json=req.coverage_details or {},
        benefits_list_json=[{"title": b} for b in (req.benefits_list or [])],
        exclusions_list_json=[{"title": e} for e in (req.exclusions_list or [])],
        required_declarations_json=[{"title": d} for d in (req.required_declarations_json or [])],
        required_documents_json=[{"title": doc} for doc in (req.required_documents or [])],
    )
    session.add(new_product)
    await session.flush()

    # Create default configuration tier
    config_tier = ProductConfiguration(
        product_id=new_product.id,
        tier_name="Standard",
        min_sum_assured=req.min_sum_assured,
        max_sum_assured=req.max_sum_assured,
        sum_assured_step=500000.0,
        term_options_json=[10, 15, 20, 25, 30],
        available_frequencies_json=["monthly", "annually"],
    )
    session.add(config_tier)

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_PRODUCT",
        resource_type="InsuranceProduct",
        resource_id=new_product.id,
        changes_json={"name": req.name, "category": req.category, "code": prod_code},
        timestamp=utc_now(),
    )
    session.add(audit)
    await session.commit()
    await session.refresh(new_product)

    return AdminProductResponse(
        id=new_product.id,
        name=new_product.name,
        category=new_product.category,
        description=new_product.description,
        base_premium=req.base_premium,
        min_sum_assured=req.min_sum_assured,
        max_sum_assured=req.max_sum_assured,
        min_age=req.min_age,
        max_age=req.max_age,
        is_active=new_product.is_active,
        coverage_details=new_product.base_rules_json,
        benefits_list=req.benefits_list,
        exclusions_list=req.exclusions_list,
        required_declarations=req.required_declarations,
        required_documents=req.required_documents,
        created_at=new_product.created_at,
        updated_at=new_product.updated_at,
    )


@router.patch("/{product_id}/status", status_code=status.HTTP_200_OK)
async def toggle_product_status(
    product_id: str,
    is_active: bool,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> dict:
    """Activate or deactivate a product."""
    p = (await session.execute(select(InsuranceProduct).where(InsuranceProduct.id == product_id))).scalar_one_or_none()
    if not p:
        raise NotFoundException(f"Insurance product '{product_id}' not found.")

    old_status = p.is_active
    p.is_active = is_active

    audit = AuditLog(
        user_id=current_user.id,
        action="TOGGLE_PRODUCT_STATUS",
        resource_type="InsuranceProduct",
        resource_id=product_id,
        changes_json={"old_active": old_status, "new_active": is_active},
        timestamp=utc_now(),
    )
    session.add(audit)
    await session.commit()

    return {"status": "success", "message": f"Product '{p.name}' active status set to {is_active}."}

