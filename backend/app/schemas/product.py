"""Pydantic schemas for Insurance Products and Configurations."""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProductConfigurationRead(BaseModel):
    id: int
    product_id: str
    tier_name: str
    min_sum_assured: float
    max_sum_assured: float
    sum_assured_step: float = 500000.0
    term_options_json: Optional[List[int]] = None
    available_frequencies_json: Optional[List[str]] = None
    riders_json: Optional[List[Dict[str, Any]]] = None

    model_config = {"from_attributes": True}


class InsuranceProductRead(BaseModel):
    id: str
    code: str
    name: str
    category: str
    description: str
    is_active: bool
    insurer_name: str = "Star Union Life & General"
    insurer_code: str = "SULG-IN"
    insurer_solvency_ratio: float = 2.15
    policy_type: str = "individual"
    base_rules_json: Optional[Dict[str, Any]] = None
    coverage_summary_json: Optional[List[str]] = None
    benefits_list_json: Optional[List[Dict[str, Any]]] = None
    exclusions_list_json: Optional[List[Dict[str, Any]]] = None
    waiting_periods_json: Optional[Dict[str, Any]] = None
    required_declarations_json: Optional[List[Dict[str, Any]]] = None
    required_documents_json: Optional[List[Dict[str, Any]]] = None
    configurations: List[ProductConfigurationRead] = []

    model_config = {"from_attributes": True}


class ProductCreate(BaseModel):
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=150)
    category: str = Field(..., max_length=50)
    description: str
    is_active: bool = True
    insurer_name: str = "Star Union Life & General"
    insurer_code: str = "SULG-IN"
    insurer_solvency_ratio: float = 2.15
    policy_type: str = "individual"
    base_rules_json: Optional[Dict[str, Any]] = None
    coverage_summary_json: Optional[List[str]] = None
    benefits_list_json: Optional[List[Dict[str, Any]]] = None
    exclusions_list_json: Optional[List[Dict[str, Any]]] = None
    waiting_periods_json: Optional[Dict[str, Any]] = None
    required_declarations_json: Optional[List[Dict[str, Any]]] = None
    required_documents_json: Optional[List[Dict[str, Any]]] = None
