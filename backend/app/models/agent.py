"""AI Agent configuration and observability execution records."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class AgentConfiguration(Base, TimestampMixin):
    __tablename__ = "agent_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_name: Mapped[str] = mapped_column(String(100), default="mistral-large-latest", nullable=False)
    system_prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    temperature: Mapped[float] = mapped_column(Numeric(3, 2), default=0.20, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)  # active, paused, disabled
    registered_tools_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    last_executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_executions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    successful_executions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_executions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    session_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True, index=True)
    input_state_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_state_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="started", nullable=False)  # started, success, failed, interrupted
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    token_usage_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation: Mapped[Optional["Conversation"]] = relationship("Conversation", back_populates="agent_executions")

