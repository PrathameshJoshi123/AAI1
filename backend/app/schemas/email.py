"""Pydantic schemas for Phase 11 Email Notification Engine and user email preferences."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserEmailPreferenceRead(BaseModel):
    id: int
    user_id: str
    notification_email: Optional[str] = None
    quote_alerts: bool
    application_updates: bool
    document_requests: bool
    marketing_consent: bool
    consent_timestamp: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserEmailPreferenceUpdate(BaseModel):
    notification_email: Optional[EmailStr] = None
    quote_alerts: Optional[bool] = None
    application_updates: Optional[bool] = None
    document_requests: Optional[bool] = None
    marketing_consent: Optional[bool] = None


class UpdateCustomerEmailRequest(BaseModel):
    email: EmailStr = Field(..., description="Valid recipient email address")


class SendQuoteEmailRequest(BaseModel):
    recipient_email: Optional[EmailStr] = Field(None, description="Optional override recipient email; defaults to customer email")


class SendTestEmailRequest(BaseModel):
    recipient_email: EmailStr = Field(..., description="Target email for diagnostic test")


class EmailDeliveryResult(BaseModel):
    success: bool
    status: str  # SENT, FAILED, NOT_CONFIGURED, SUPPRESSED_NO_CONSENT
    message: str
    delivery_log_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class EmailDeliveryLogRead(BaseModel):
    id: int
    user_id: Optional[str] = None
    recipient_email: str
    subject: str
    template_name: str
    status: str
    error_message: Optional[str] = None
    payload_json: Optional[Dict[str, Any]] = None
    sent_at: Optional[datetime] = None
    retry_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedEmailLogsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[EmailDeliveryLogRead]

