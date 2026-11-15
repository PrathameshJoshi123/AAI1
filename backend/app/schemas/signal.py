"""Pydantic schemas for Behavioral Signal Ingestion."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SignalIngestRequest(BaseModel):
    session_id: str = Field(..., min_length=4, max_length=100)
    prospect_id: Optional[str] = None
    signal_type: str = Field(
        ...,
        pattern=r"^(page_view|time_on_page|quote_attempt|coverage_calculator_used|comparison_viewed|faq_opened|drop_off_step|chat_initiated)$"
    )
    payload_json: Optional[Dict[str, Any]] = Field(default_factory=dict)
    client_timestamp: Optional[datetime] = None


class BatchSignalIngestRequest(BaseModel):
    events: List[SignalIngestRequest] = Field(..., min_length=1, max_length=50)


class BehavioralSignalRead(BaseModel):
    id: int
    prospect_id: str
    session_id: str
    signal_type: str
    payload_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}

