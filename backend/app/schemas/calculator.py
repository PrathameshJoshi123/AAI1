"""Actuarial and Deterministic Coverage Calculator Schemas."""
from typing import Any, Dict
from pydantic import BaseModel, Field


class HLVCalculationRequest(BaseModel):
    annual_income: float = Field(..., ge=100000, description="Annual earned income in INR")
    current_age: int = Field(..., ge=18, le=65)
    retirement_age: int = Field(60, ge=45, le=75)
    annual_household_expenses: float = Field(..., ge=50000)
    outstanding_liabilities: float = Field(0.0, ge=0, description="Home loans, personal loans, vehicle loans")
    current_liquid_investments: float = Field(0.0, ge=0, description="Mutual funds, FD, existing life cover")
    inflation_rate_percent: float = Field(6.0, ge=3.0, le=12.0)


class HLVCalculationResponse(BaseModel):
    methodology: str = "Human Life Value (Income Replacement & Expense Capitalization Model)"
    recommended_term_cover: float
    human_life_value_raw: float
    outstanding_liabilities_component: float
    existing_cover_offset: float
    net_protection_gap: float
    rule_of_thumb_multiplier: str
    calculation_breakdown: Dict[str, Any]
    formula_explanation: str

