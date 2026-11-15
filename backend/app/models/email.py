"""Email delivery logs and user notification preferences models."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.models.auth import User


class EmailDeliveryLog(Base, TimestampMixin):
    """Immutable audit trail for all outbound transactional email notifications."""
    __tablename__ = "email_delivery_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    recipient_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    template_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # PENDING, SENT, FAILED, NOT_CONFIGURED, SUPPRESSED_NO_CONSENT
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    payload_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[Optional["User"]] = relationship("User")


class UserEmailPreference(Base, TimestampMixin):
    """Customer-managed granular email notification preferences and consent."""
    __tablename__ = "user_email_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    notification_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    quote_alerts: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    application_updates: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    document_requests: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    marketing_consent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    consent_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User")

