"""Pydantic schemas for Underwriting Cases, Reviews, and Case Notes."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class UnderwritingReviewCreate(BaseModel):
    decision: str = Field(..., pattern="^(approved_standard|approved_with_loading|declined|more_info_needed)$")
    review_type: str = Field(default="initial_assessment", pattern="^(initial_assessment|medical_evaluation|financial_scrutiny|supervisor_escalation)$")
    loading_percentage: float = Field(default=0.0, ge=0.0, le=200.0)
    notes: str = Field(..., min_length=5)
    conditions: Optional[str] = None


class UnderwritingReviewRead(BaseModel):
    id: int
    case_id: str
    reviewer_id: str
    review_type: str
    decision: str
    loading_percentage: float
    notes: str
    conditions: Optional[str] = None
    reviewed_at: datetime

    model_config = {"from_attributes": True}


class CaseNoteCreate(BaseModel):
    note_type: str = Field(default="internal_note", pattern="^(internal_note|inquiry|underwriter_query|customer_communication)$")
    content: str = Field(..., min_length=3)
    is_confidential: bool = False


class CaseNoteRead(BaseModel):
    id: str
    case_id: str
    author_id: str
    author_name: str
    author_role: str
    note_type: str
    content: str
    is_confidential: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskFlagItem(BaseModel):
    category: str  # medical, financial, lifestyle, identity
    severity: str  # low, medium, high, critical
    flag: str
    source: str


class UnderwritingCaseSummaryRead(BaseModel):
    id: str
    case_number: str
    application_id: str
    customer_id: str
    customer_name: str
    product_name: str
    sum_assured: float
    total_premium: float
    priority: str
    risk_rating: str
    status: str
    sla_deadline: Optional[datetime] = None
    sla_hours_remaining: Optional[float] = None
    risk_flags_count: int = 0
    assigned_advisor_name: Optional[str] = None
    assigned_underwriter_name: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UnderwritingCaseRead(BaseModel):
    id: str
    case_number: str
    application_id: str
    customer_id: str
    assigned_advisor_id: Optional[str] = None
    assigned_underwriter_id: Optional[str] = None
    priority: str = "medium"
    risk_rating: str = "standard"
    status: str = "assigned"
    sla_deadline: Optional[datetime] = None
    risk_flags_json: Optional[List[Dict[str, Any]]] = None
    medical_risk_summary: Optional[str] = None
    financial_risk_summary: Optional[str] = None
    created_at: datetime
    reviews: List[UnderwritingReviewRead] = []

    model_config = {"from_attributes": True}


class UnderwritingCaseDetailRead(BaseModel):
    id: str
    case_number: str
    application_id: str
    customer_id: str
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    customer_dob: Optional[str] = None
    customer_city: Optional[str] = None
    product_id: Optional[str] = None
    product_name: str
    product_category: str
    sum_assured: float
    policy_term_years: int
    total_premium: float
    priority: str
    risk_rating: str
    status: str
    sla_deadline: Optional[datetime] = None
    sla_hours_remaining: Optional[float] = None
    risk_flags: List[RiskFlagItem] = Field(default_factory=list)
    medical_risk_summary: Optional[str] = None  # Redacted if user lacks medical_data:view
    financial_risk_summary: Optional[str] = None
    proposal_data: Optional[Dict[str, Any]] = None
    proposal_checksum: Optional[str] = None
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    reviews: List[UnderwritingReviewRead] = Field(default_factory=list)
    notes: List[CaseNoteRead] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentVerificationActionRequest(BaseModel):
    verification_notes: Optional[str] = None


class DocumentRejectionActionRequest(BaseModel):
    rejection_reason_code: str = Field(..., pattern="^(ILLEGIBLE_SCAN|EXPIRED_DOCUMENT|NAME_MISMATCH|INCOMPLETE_PAGES|FRAUD_SUSPICION|OTHER)$")
    detailed_instructions: str = Field(..., min_length=5)


class MoreInfoNeededRequest(BaseModel):
    notes: str = Field(..., min_length=10)
    requested_documents: List[str] = Field(default_factory=list)
