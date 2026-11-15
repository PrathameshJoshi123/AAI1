"""Customer Journey Lifecycle and Resumption Schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class JourneyStatusResponse(BaseModel):
    customer_id: str
    current_stage: str = Field(..., description="discovery, needs_assessment, product_matching, quote_review, proposal_draft, submitted")
    active_conversation_id: Optional[str]
    has_active_quote: bool
    active_quote_id: Optional[str]
    has_active_application: bool
    active_application_id: Optional[str]
    qualification_completed: bool
    qualification_data: Optional[Dict[str, Any]] = None
    missing_requirements: List[str]
    last_activity_at: datetime


class JourneyTransitionRequest(BaseModel):
    target_stage: str = Field(..., pattern=r"^(discovery|needs_assessment|product_matching|quote_review|proposal_draft|submitted)$")
    context_data: Optional[Dict[str, Any]] = None


class ResumeJourneyResponse(BaseModel):
    thread_id: str
    conversation_id: str
    stage: str
    last_message: Optional[str]
    suggested_action: str
    qualification_snapshot: Dict[str, Any]

