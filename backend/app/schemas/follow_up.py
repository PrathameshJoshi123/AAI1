"""Pydantic schemas for Follow-up Management."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FollowUpCreate(BaseModel):
    customer_id: Optional[str] = None
    prospect_id: Optional[str] = None
    assigned_advisor_id: Optional[str] = None
    due_date: datetime
    channel: str = Field(default="phone", pattern="^(phone|email|chat|meeting)$")
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    notes: Optional[str] = None


class FollowUpUpdate(BaseModel):
    due_date: Optional[datetime] = None
    channel: Optional[str] = Field(None, pattern="^(phone|email|chat|meeting)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    status: Optional[str] = Field(None, pattern="^(pending|completed|cancelled)$")
    notes: Optional[str] = None


class FollowUpRead(BaseModel):
    id: int
    customer_id: Optional[str] = None
    prospect_id: Optional[str] = None
    assigned_advisor_id: str
    target_name: Optional[str] = None
    target_contact: Optional[str] = None
    due_date: datetime
    channel: str
    status: str
    priority: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

