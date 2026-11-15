"""Pydantic schemas for Admin & Owner Dashboard (Phase 9)."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------
# Executive Overview
# ---------------------------------------------------------

class ExecutiveMetricsResponse(BaseModel):
    total_prospects: int
    qualified_leads: int
    active_conversations: int
    quotes_generated: int
    applications_submitted: int
    applications_awaiting_review: int
    conversion_rate: float = Field(..., description="Percentage of submitted apps vs total prospects")
    pending_follow_ups: int


class RecentActivityItem(BaseModel):
    id: str
    action: str
    resource_type: str
    resource_id: str
    actor_email: Optional[str] = None
    description: str
    timestamp: datetime


class RecentActivityResponse(BaseModel):
    activities: List[RecentActivityItem]
    total: int


class AdminCustomerItem(BaseModel):
    id: str
    user_id: str
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    onboarding_stage: str
    risk_tier: str
    annual_income: Optional[float] = None
    occupation: Optional[str] = None
    assigned_advisor_name: Optional[str] = None
    created_at: datetime


# ---------------------------------------------------------
# Business Analytics & Conversion Funnel
# ---------------------------------------------------------

class ChannelPerformanceItem(BaseModel):
    channel: str
    total_leads: int
    qualified_leads: int
    avg_score: float
    applications_submitted: int
    conversion_rate: float


class ProductPerformanceItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    quotes_count: int
    applications_count: int
    approved_count: int
    conversion_rate: float
    total_estimated_premium: float


class AdvisorPerformanceItem(BaseModel):
    advisor_id: str
    advisor_name: str
    email: str
    active_cases: int
    completed_reviews: int
    pending_follow_ups: int
    conversion_rate: float
    is_available: bool


class TurnaroundAnalyticsResponse(BaseModel):
    avg_hours_to_quote: float
    avg_hours_to_submission: float
    avg_hours_to_underwriting_decision: float
    sla_compliance_percentage: float


class FunnelStage(BaseModel):
    stage_key: str
    label: str
    count: int
    conversion_from_prev: float
    drop_off_count: int


class ConversionFunnelResponse(BaseModel):
    stages: List[FunnelStage]
    overall_conversion: float


# ---------------------------------------------------------
# Agent Control Centre
# ---------------------------------------------------------

class AgentTelemetryResponse(BaseModel):
    id: int
    agent_name: str
    description: Optional[str] = None
    model_name: str
    temperature: float
    is_active: bool
    status: str = Field(..., description="active, paused, disabled")
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_latency_ms: Optional[int] = None
    last_executed_at: Optional[datetime] = None


class AgentStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="active, paused, disabled")


class AgentExecutionLogItem(BaseModel):
    id: str
    session_id: str
    conversation_id: Optional[str] = None
    status: str
    latency_ms: Optional[int] = None
    input_state: Dict[str, Any]
    output_state: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    executed_at: datetime


class AgentExecutionLogsResponse(BaseModel):
    agent_name: str
    executions: List[AgentExecutionLogItem]
    total: int


# ---------------------------------------------------------
# Employee Management
# ---------------------------------------------------------

class EmployeeCreateRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    role_names: List[str] = Field(..., description="Advisor, Underwriter, Admin, Owner")
    
    # Advisor specific
    license_number: Optional[str] = None
    specializations: Optional[str] = None
    max_active_cases: Optional[int] = 50
    
    # Underwriter specific
    authority_level: Optional[str] = "Level 1"
    max_coverage_limit: Optional[float] = 500000.0


class EmployeeStatusUpdateRequest(BaseModel):
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None  # for advisor


class EmployeeRoleUpdateRequest(BaseModel):
    role_names: List[str]


class EmployeeResponse(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool
    roles: List[str]
    created_at: datetime
    
    # Advisor details
    advisor_id: Optional[str] = None
    license_number: Optional[str] = None
    specializations: Optional[str] = None
    max_active_cases: Optional[int] = None
    active_cases_count: Optional[int] = None
    is_available: Optional[bool] = None
    
    # Underwriter details
    underwriter_id: Optional[str] = None
    authority_level: Optional[str] = None
    max_coverage_limit: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Product Catalog Administration
# ---------------------------------------------------------

class AdminProductCreateRequest(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    base_premium: float
    min_sum_assured: float
    max_sum_assured: float
    min_age: int = 18
    max_age: int = 65
    is_active: bool = True
    coverage_details: Optional[Dict[str, Any]] = None
    benefits_list: Optional[List[str]] = None
    exclusions_list: Optional[List[str]] = None
    required_declarations: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None


class AdminProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    base_premium: Optional[float] = None
    min_sum_assured: Optional[float] = None
    max_sum_assured: Optional[float] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    is_active: Optional[bool] = None
    coverage_details: Optional[Dict[str, Any]] = None
    benefits_list: Optional[List[str]] = None
    exclusions_list: Optional[List[str]] = None
    required_declarations: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None


class AdminProductResponse(BaseModel):
    id: str
    name: str
    category: str
    description: Optional[str] = None
    base_premium: float
    min_sum_assured: float
    max_sum_assured: float
    min_age: int
    max_age: int
    is_active: bool
    coverage_details: Optional[Dict[str, Any]] = None
    benefits_list: Optional[List[str]] = None
    exclusions_list: Optional[List[str]] = None
    required_declarations: Optional[List[str]] = None
    required_documents: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# Compliance & Audit Vault
# ---------------------------------------------------------

class AuditLogItem(BaseModel):
    id: int
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: str
    ip_address: Optional[str] = None
    changes_json: Optional[Dict[str, Any]] = None
    timestamp: datetime


class AuditLogSearchResponse(BaseModel):
    records: List[AuditLogItem]
    total: int
    page: int
    size: int


# ---------------------------------------------------------
# Integration Health Management
# ---------------------------------------------------------

class IntegrationHealthItem(BaseModel):
    service_key: str
    name: str
    category: str = Field(..., description="ai, comms, insurer, storage")
    status: str = Field(..., description="active, warning, error, not_configured")
    details: str
    last_checked_at: datetime
    endpoint_or_host: Optional[str] = None


class IntegrationHealthResponse(BaseModel):
    integrations: List[IntegrationHealthItem]


# ---------------------------------------------------------
# Dynamic System Settings
# ---------------------------------------------------------

class SystemSettingResponse(BaseModel):
    id: int
    key: str
    value_json: Dict[str, Any]
    description: Optional[str] = None
    updated_at: datetime


class SystemSettingUpdateRequest(BaseModel):
    value_json: Dict[str, Any]
    description: Optional[str] = None
