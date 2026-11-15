"""Notifications, scheduled follow-ups, and dynamic system settings."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, utc_now

if TYPE_CHECKING:
    from app.models.profile import Customer, Advisor
    from app.models.prospect import Prospect
    from app.models.auth import User


class FollowUp(Base, TimestampMixin):
    __tablename__ = "follow_ups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    prospect_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("prospects.id", ondelete="CASCADE"), nullable=True, index=True)
    assigned_advisor_id: Mapped[str] = mapped_column(String(36), ForeignKey("advisors.id", ondelete="CASCADE"), nullable=False, index=True)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), default="phone", nullable=False)  # phone, email, chat
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)  # pending, completed, cancelled
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="follow_ups")
    prospect: Mapped[Optional["Prospect"]] = relationship("Prospect", back_populates="follow_ups")
    assigned_advisor: Mapped["Advisor"] = relationship("Advisor", back_populates="follow_ups")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)  # case_update, quote_ready, alert
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    link_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship("User")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    value_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

