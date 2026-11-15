"""Domain profile models for Customer, Advisor, and Underwriter."""
from datetime import date
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.auth import User
    from app.models.conversation import Conversation
    from app.models.recommendation import CustomerQualification, Recommendation, Quote
    from app.models.application import Application, ApplicationDocument
    from app.models.underwriting import UnderwritingCase
    from app.models.system import FollowUp
    from app.models.prospect import Prospect


class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    annual_income: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    health_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    risk_tier: Mapped[str] = mapped_column(String(30), default="standard", nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tobacco_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    onboarding_stage: Mapped[str] = mapped_column(String(50), default="discovery", nullable=False)
    active_conversation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    assigned_advisor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("advisors.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="customer")
    assigned_advisor: Mapped[Optional["Advisor"]] = relationship("Advisor", back_populates="assigned_customers", foreign_keys=[assigned_advisor_id])
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="customer", cascade="all, delete-orphan")
    qualifications: Mapped[List["CustomerQualification"]] = relationship("CustomerQualification", back_populates="customer", cascade="all, delete-orphan")
    recommendations: Mapped[List["Recommendation"]] = relationship("Recommendation", back_populates="customer", cascade="all, delete-orphan")
    quotes: Mapped[List["Quote"]] = relationship("Quote", back_populates="customer", cascade="all, delete-orphan")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="customer", cascade="all, delete-orphan")
    documents: Mapped[List["ApplicationDocument"]] = relationship("ApplicationDocument", back_populates="customer", cascade="all, delete-orphan")
    underwriting_cases: Mapped[List["UnderwritingCase"]] = relationship("UnderwritingCase", back_populates="customer", cascade="all, delete-orphan")
    follow_ups: Mapped[List["FollowUp"]] = relationship("FollowUp", back_populates="customer", cascade="all, delete-orphan")


class Advisor(Base, TimestampMixin):
    __tablename__ = "advisors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    specializations: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    max_active_cases: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="advisor")
    assigned_customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="assigned_advisor", foreign_keys=[Customer.assigned_advisor_id])
    assigned_prospects: Mapped[List["Prospect"]] = relationship("Prospect", back_populates="assigned_advisor", foreign_keys="Prospect.assigned_advisor_id")
    assigned_cases: Mapped[List["UnderwritingCase"]] = relationship("UnderwritingCase", back_populates="assigned_advisor")
    follow_ups: Mapped[List["FollowUp"]] = relationship("FollowUp", back_populates="assigned_advisor")


class Underwriter(Base, TimestampMixin):
    __tablename__ = "underwriters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    authority_level: Mapped[str] = mapped_column(String(50), default="Level 1", nullable=False)
    max_coverage_limit: Mapped[float] = mapped_column(Numeric(14, 2), default=500000.00, nullable=False)
    license_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="underwriter")
    assigned_cases: Mapped[List["UnderwritingCase"]] = relationship("UnderwritingCase", back_populates="assigned_underwriter")

