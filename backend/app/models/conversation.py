"""Conversations and messaging history models."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.profile import Customer
    from app.models.prospect import Prospect
    from app.models.recommendation import Recommendation
    from app.models.agent import AgentExecution


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    prospect_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("prospects.id", ondelete="CASCADE"), nullable=True, index=True)
    channel: Mapped[str] = mapped_column(String(30), default="web_chat", nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)  # active, closed, escalated
    thread_title: Mapped[str] = mapped_column(String(150), default="Insurance Advisory Consultation", nullable=False)
    conversation_mode: Mapped[str] = mapped_column(String(30), default="general_advisory", nullable=False)
    summary_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_turn_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="conversations")
    prospect: Mapped[Optional["Prospect"]] = relationship("Prospect", back_populates="conversations")
    messages: Mapped[List["ConversationMessage"]] = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ConversationMessage.created_at")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="conversation")
    agent_executions: Mapped[List["AgentExecution"]] = relationship("AgentExecution", back_populates="conversation")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_type: Mapped[str] = mapped_column(String(20), nullable=False)  # user, agent, advisor, system
    sender_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message_type: Mapped[str] = mapped_column(String(30), default="text", nullable=False)  # text, suggested_chips, form_widget, quote_preview, disclaimer
    content: Mapped[str] = mapped_column(Text, nullable=False)
    widget_data_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")

