"""Underwriting cases, assignments, and medical/financial reviews."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.profile import Customer, Advisor, Underwriter
    from app.models.application import Application
    from app.models.auth import User


class UnderwritingCase(Base, TimestampMixin):
    __tablename__ = "underwriting_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_advisor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("advisors.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_underwriter_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("underwriters.id", ondelete="SET NULL"), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)  # low, medium, high, urgent
    risk_rating: Mapped[str] = mapped_column(String(30), default="standard", nullable=False)  # preferred, standard, substandard, decline
    status: Mapped[str] = mapped_column(String(50), default="assigned", nullable=False)  # assigned, in_review, more_info_needed, escalated, approved, declined
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    risk_flags_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    medical_risk_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    financial_risk_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    application: Mapped["Application"] = relationship("Application", back_populates="underwriting_case")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="underwriting_cases")
    assigned_advisor: Mapped[Optional["Advisor"]] = relationship("Advisor", back_populates="assigned_cases")
    assigned_underwriter: Mapped[Optional["Underwriter"]] = relationship("Underwriter", back_populates="assigned_cases")
    reviews: Mapped[List["UnderwritingReview"]] = relationship("UnderwritingReview", back_populates="case", cascade="all, delete-orphan", order_by="UnderwritingReview.reviewed_at")
    case_notes: Mapped[List["CaseNote"]] = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan", order_by="CaseNote.created_at.desc()")


class UnderwritingReview(Base):
    __tablename__ = "underwriting_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("underwriting_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)  # initial_assessment, medical_evaluation, financial_scrutiny, supervisor_escalation
    decision: Mapped[str] = mapped_column(String(50), nullable=False)  # approved_standard, approved_with_loading, declined, more_info_needed
    loading_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    case: Mapped["UnderwritingCase"] = relationship("UnderwritingCase", back_populates="reviews")
    reviewer: Mapped["User"] = relationship("User")


class CaseNote(Base, TimestampMixin):
    __tablename__ = "case_notes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("underwriting_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    note_type: Mapped[str] = mapped_column(String(30), default="internal_note", nullable=False)  # internal_note, inquiry, underwriter_query, customer_communication
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    case: Mapped["UnderwritingCase"] = relationship("UnderwritingCase", back_populates="case_notes")
    author: Mapped["User"] = relationship("User")
