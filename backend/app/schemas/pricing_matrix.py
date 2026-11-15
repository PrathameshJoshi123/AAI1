"""Pydantic schemas for Actuarial Pricing Matrices."""
from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class PricingMatrixRead(BaseModel):
    id: str
    product_id: str
    matrix_version: str
    is_active: bool
    effective_from: datetime
    effective_to: Optional[datetime] = None
    age_band_rates_json: Dict[str, float]
    gender_multipliers_json: Dict[str, float]
    smoker_loading_factors_json: Dict[str, float]
    frequency_multipliers_json: Dict[str, float]
    health_tier_loadings_json: Dict[str, float]
    rider_rate_cards_json: Dict[str, Any]
    tax_rate_percent: float
    created_at: datetime

    model_config = {"from_attributes": True}


class PricingMatrixCreate(BaseModel):
    product_id: str
    matrix_version: str = Field(..., max_length=50)
    is_active: bool = True
    age_band_rates_json: Dict[str, float]
    gender_multipliers_json: Dict[str, float]
    smoker_loading_factors_json: Dict[str, float]
    frequency_multipliers_json: Dict[str, float]
    health_tier_loadings_json: Dict[str, float]
    rider_rate_cards_json: Dict[str, Any]
    tax_rate_percent: float = 18.00

