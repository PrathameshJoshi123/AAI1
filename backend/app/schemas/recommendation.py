"""Pydantic schemas for Policy Recommendations."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RecommendationCreate(BaseModel):
    customer_id: Optional[str] = None
    target_category: Optional[str] = None  # term_life, health, motor
    recommended_sum_assured: Optional[float] = None


class RecommendationRead(BaseModel):
    id: str
    customer_id: str
    conversation_id: Optional[str] = None
    recommended_product_id: str
    configuration_id: Optional[int] = None
    match_score: float
    recommended_sum_assured: float
    recommended_term_years: int
    rationale: str
    match_factors_json: Optional[Dict[str, Any]] = None
    assumptions_json: Optional[List[str]] = None
    limitations_json: Optional[List[str]] = None
    alternative_options_json: Optional[List[Dict[str, Any]]] = None
    status: str
    created_at: datetime

    # Nested product details for UI convenience
    product_name: Optional[str] = None
    product_code: Optional[str] = None
    product_category: Optional[str] = None
    insurer_name: Optional[str] = None
    insurer_solvency_ratio: Optional[float] = None

    model_config = {"from_attributes": True}


class RecommendationEvaluateResponse(BaseModel):
    recommendations: List[RecommendationRead]
    primary_recommendation: Optional[RecommendationRead] = None
    target_category: str
    recommended_sum_assured: float
    disclaimer: str = (
        "Recommendations are derived deterministically based on your stated financial "
        "and health declarations. Final coverage eligibility is confirmed during underwriting."
    )

