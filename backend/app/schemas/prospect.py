"""Pydantic schemas for Prospects, Leads, and Pipeline Management."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class ProspectCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=30)
    source_name: str = Field("web_direct", max_length=50)
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    utm_term: Optional[str] = None
    utm_content: Optional[str] = None
    target_insurance_type: Optional[str] = None
    initial_session_id: Optional[str] = None
    estimated_budget_min: Optional[float] = None
    estimated_budget_max: Optional[float] = None


class ProspectUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = Field(None, pattern=r"^(new|engaged|qualified|converted|dropped)$")
    target_insurance_type: Optional[str] = None
    estimated_budget_min: Optional[float] = None
    estimated_budget_max: Optional[float] = None


class ProspectFilterParams(BaseModel):
    query: Optional[str] = None
    status: Optional[List[str]] = None
    segment: Optional[List[str]] = None
    source_id: Optional[int] = None
    assigned_advisor_id: Optional[str] = None
    unassigned_only: bool = False
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    consented_only: bool = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: str = Field("last_activity_at", pattern=r"^(last_activity_at|created_at|name|status|segment)$")
    sort_order: str = Field("desc", pattern=r"^(asc|desc)$")


class ScoreFactorRead(BaseModel):
    rule_code: str
    rule_name: str
    category: str
    points_awarded: int
    rationale: str


class LeadScoreRead(BaseModel):
    id: Optional[int] = None
    score: float
    calculated_at: datetime
    factors: List[ScoreFactorRead] = Field(default_factory=list)


class ProspectRead(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    segment: str
    source_name: Optional[str] = None
    target_insurance_type: Optional[str] = None
    assigned_advisor_id: Optional[str] = None
    assigned_advisor_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    latest_score: Optional[float] = None
    can_contact: bool = False
    created_at: datetime
    last_activity_at: datetime

    model_config = {"from_attributes": True}


class ProspectDetailRead(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    status: str
    segment: str
    source_id: Optional[int] = None
    source_name: Optional[str] = None
    channel_type: Optional[str] = None
    target_insurance_type: Optional[str] = None
    estimated_budget_min: Optional[float] = None
    estimated_budget_max: Optional[float] = None
    assigned_advisor_id: Optional[str] = None
    assigned_advisor_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    created_at: datetime
    last_activity_at: datetime
    latest_score: Optional[LeadScoreRead] = None
    active_consents: List[str] = Field(default_factory=list)
    can_contact: bool = False
    signals_count: int = 0

    model_config = {"from_attributes": True}


class AdvisorAssignRequest(BaseModel):
    advisor_id: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)


class AdvisorOutreachNoteCreate(BaseModel):
    outcome: str = Field(..., pattern=r"^(connected_interested|callback_requested|unreachable|not_interested|info_provided)$")
    notes: str = Field(..., min_length=3, max_length=1000)
    schedule_follow_up: bool = False
    follow_up_date: Optional[datetime] = None
    follow_up_channel: str = Field("phone", pattern=r"^(phone|email|chat)$")


class PipelineKPIsRead(BaseModel):
    total_prospects: int
    status_breakdown: Dict[str, int]
    segment_breakdown: Dict[str, int]
    unassigned_leads: int
