"""Prospect, lead acquisition, and behavioral signal tracking models."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid, utc_now

if TYPE_CHECKING:
    from app.models.profile import Customer, Advisor
    from app.models.conversation import Conversation
    from app.models.recommendation import CustomerQualification
    from app.models.audit import ConsentRecord
    from app.models.system import FollowUp


class LeadSource(Base, TimestampMixin):
    __tablename__ = "lead_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    channel_type: Mapped[str] = mapped_column(String(50), nullable=False)  # web, mobile, partner, organic
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    prospects: Mapped[List["Prospect"]] = relationship("Prospect", back_populates="source")


class LeadScoringRule(Base, TimestampMixin):
    __tablename__ = "lead_scoring_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # profile, intent, engagement, consent, penalty
    rule_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    point_value: Mapped[int] = mapped_column(Integer, nullable=False)  # e.g. +25 or -50
    condition_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Prospect(Base, TimestampMixin):
    __tablename__ = "prospects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("lead_sources.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)  # new, engaged, qualified, converted, dropped
    converted_customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    assigned_advisor_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("advisors.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    segment: Mapped[str] = mapped_column(String(50), default="top_of_funnel", nullable=False, index=True)  # top_of_funnel, warm_consideration, high_intent, price_sensitive, dormant
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    estimated_budget_min: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    estimated_budget_max: Mapped[Optional[float]] = mapped_column(Numeric(12, 2), nullable=True)
    target_insurance_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # term_life, health, motor

    # Relationships
    source: Mapped[Optional["LeadSource"]] = relationship("LeadSource", back_populates="prospects")
    converted_customer: Mapped[Optional["Customer"]] = relationship("Customer", foreign_keys=[converted_customer_id])
    assigned_advisor: Mapped[Optional["Advisor"]] = relationship("Advisor", foreign_keys=[assigned_advisor_id], back_populates="assigned_prospects")
    signals: Mapped[List["BehavioralSignal"]] = relationship("BehavioralSignal", back_populates="prospect", cascade="all, delete-orphan")
    lead_scores: Mapped[List["LeadScore"]] = relationship("LeadScore", back_populates="prospect", cascade="all, delete-orphan")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="prospect")
    qualifications: Mapped[List["CustomerQualification"]] = relationship("CustomerQualification", back_populates="prospect")
    consents: Mapped[List["ConsentRecord"]] = relationship("ConsentRecord", back_populates="prospect")
    follow_ups: Mapped[List["FollowUp"]] = relationship("FollowUp", back_populates="prospect")


class BehavioralSignal(Base):
    __tablename__ = "behavioral_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prospect_id: Mapped[str] = mapped_column(String(36), ForeignKey("prospects.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)  # page_view, quote_attempt, time_on_page
    payload_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    prospect: Mapped["Prospect"] = relationship("Prospect", back_populates="signals")


class LeadScore(Base):
    __tablename__ = "lead_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    prospect_id: Mapped[str] = mapped_column(String(36), ForeignKey("prospects.id", ondelete="CASCADE"), nullable=False, index=True)
    score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # 0.00 to 100.00
    score_factors_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    prospect: Mapped["Prospect"] = relationship("Prospect", back_populates="lead_scores")
