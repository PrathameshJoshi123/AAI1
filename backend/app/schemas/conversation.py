"""Conversation turns, messages, and widget payloads schemas."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WidgetDataPayload(BaseModel):
    widget_type: str = Field(..., pattern=r"^(coverage_slider|category_picker|tobacco_toggle|family_counter|quote_card)$")
    title: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    submit_action_url: Optional[str] = None


class CustomerChatTurnRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID or null to initiate a new thread")
    message: str = Field(..., min_length=1, max_length=2000, description="Customer message or selected chip response")
    language: str = Field("en", pattern=r"^(en|hi)$", description="Language preference for conversational response")
    client_context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Active client viewport context")


class ConversationMessageRead(BaseModel):
    id: int
    conversation_id: str
    sender_type: str = Field(..., pattern=r"^(user|agent|advisor|system)$")
    sender_name: str
    content: str
    message_type: str = Field("text", pattern=r"^(text|suggested_chips|form_widget|quote_preview|disclaimer)$")
    suggested_chips: Optional[List[str]] = None
    widget_data: Optional[WidgetDataPayload] = None
    action_buttons: Optional[List[Dict[str, Any]]] = None
    created_at: datetime


class ConversationThreadRead(BaseModel):
    id: str
    customer_id: Optional[str] = None
    title: str
    status: str
    mode: str
    messages: List[ConversationMessageRead]
    created_at: datetime
    last_turn_at: datetime

