"""Pydantic schemas for Quotes and Actuarial Calculations."""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class QuoteCreate(BaseModel):
    product_id: str
    configuration_id: Optional[int] = None
    sum_assured: float = Field(..., gt=0)
    policy_term_years: int = Field(..., gt=0, le=50)
    payment_frequency: Literal["monthly", "quarterly", "half_yearly", "annually"] = Field(default="annually")
    selected_rider_codes: List[str] = Field(default_factory=list)
    customer_id: Optional[str] = None  # Inferred from JWT for customers


class QuoteRecalculateRequest(BaseModel):
    sum_assured: float = Field(..., gt=0)
    policy_term_years: int = Field(..., gt=0, le=50)
    payment_frequency: Literal["monthly", "quarterly", "half_yearly", "annually"] = "annually"
    selected_rider_codes: List[str] = Field(default_factory=list)


class QuoteRead(BaseModel):
    id: str
    quote_number: str
    customer_id: str
    product_id: str
    configuration_id: Optional[int] = None
    pricing_matrix_version: str = "v1.0.0-actuarial-2026"
    sum_assured: float
    policy_term_years: int
    payment_frequency: str
    selected_riders_json: Optional[List[Dict[str, Any]]] = None
    base_premium: float
    health_loading_amount: float = 0.0
    rider_premium: float = 0.0
    net_premium: float = 0.0
    tax_amount: float
    total_premium: float
    calculation_breakdown_json: Optional[Dict[str, Any]] = None
    expires_at: datetime
    status: str
    created_at: datetime
    disclaimer: str = (
        "Indicative quote only. Final premium and policy terms are subject to formal "
        "underwriting review and insurer acceptance."
    )

    model_config = {"from_attributes": True}
