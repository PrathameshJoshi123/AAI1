"""Admin Actuarial Pricing Matrix Management Endpoints."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_roles
from app.core.exceptions import EntityNotFoundException
from app.models.auth import User
from app.models.pricing_matrix import ProductPricingMatrix
from app.repositories.pricing_matrix_repository import PricingMatrixRepository
from app.schemas.common import APIResponse
from app.schemas.pricing_matrix import PricingMatrixCreate, PricingMatrixRead

router = APIRouter(prefix="/admin/pricing-matrices", tags=["Admin Pricing Matrices"])


@router.get("/product/{product_id}", response_model=APIResponse[List[PricingMatrixRead]])
async def list_matrices_for_product(
    product_id: str,
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """List all actuarial pricing matrices for a product."""
    repo = PricingMatrixRepository(session)
    matrices = await repo.list_for_product(product_id)
    return APIResponse(
        data=[PricingMatrixRead.model_validate(m) for m in matrices]
    )


@router.post("", response_model=APIResponse[PricingMatrixRead], status_code=status.HTTP_201_CREATED)
async def create_pricing_matrix(
    data: PricingMatrixCreate,
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Publish a new versioned actuarial rate matrix (Restricted to Admin / Owner)."""
    repo = PricingMatrixRepository(session)
    matrix = ProductPricingMatrix(
        product_id=data.product_id,
        matrix_version=data.matrix_version,
        is_active=data.is_active,
        age_band_rates_json=data.age_band_rates_json,
        gender_multipliers_json=data.gender_multipliers_json,
        smoker_loading_factors_json=data.smoker_loading_factors_json,
        frequency_multipliers_json=data.frequency_multipliers_json,
        health_tier_loadings_json=data.health_tier_loadings_json,
        rider_rate_cards_json=data.rider_rate_cards_json,
        tax_rate_percent=data.tax_rate_percent,
    )
    created = await repo.create(matrix)
    return APIResponse(
        data=PricingMatrixRead.model_validate(created),
        message="Actuarial pricing matrix created and activated.",
    )

