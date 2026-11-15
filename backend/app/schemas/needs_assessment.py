"""Structured Needs Assessment Request and Response Schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NeedsAssessmentSubmit(BaseModel):
    category: str = Field("term_life", pattern=r"^(term_life|health|motor)$")
    age: int = Field(..., ge=18, le=80, description="Age of the primary insured")
    annual_income: float = Field(..., ge=0, description="Gross annual income in INR")
    dependents_count: int = Field(0, ge=0, le=10, description="Number of financially dependent members")
    marital_status: str = Field("single", pattern=r"^(single|married|divorced|widowed)$")
    occupation: str = Field(..., max_length=100)
    tobacco_user: bool = Field(False, description="Tobacco/nicotine consumption in past 36 months")
    has_pre_existing_conditions: bool = Field(False)
    pre_existing_conditions_details: Optional[str] = Field(None, max_length=500)
    existing_life_cover: float = Field(0.0, ge=0)
    existing_health_cover: float = Field(0.0, ge=0)
    desired_coverage_amount: Optional[float] = Field(None, ge=100000)


class NeedsAssessmentResponse(BaseModel):
    qualification_id: str
    customer_id: str
    category: str
    eligibility_status: str
    calculated_coverage_gap: float
    recommended_sum_assured: float
    health_risk_tier: str
    key_observations: List[str]
    qualifying_products_count: int
    factors: Dict[str, Any]
    created_at: datetime

