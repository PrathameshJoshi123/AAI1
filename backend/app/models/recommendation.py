"""Customer qualifications, product recommendations, and binding quotes."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.profile import Customer
    from app.models.prospect import Prospect
    from app.models.conversation import Conversation
    from app.models.product import InsuranceProduct, ProductConfiguration
    from app.models.application import Application


class CustomerQualification(Base, TimestampMixin):
    __tablename__ = "customer_qualifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True, index=True)
    prospect_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("prospects.id", ondelete="CASCADE"), nullable=True, index=True)
    eligibility_status: Mapped[str] = mapped_column(String(30), default="in_progress", nullable=False)  # eligible, ineligible, needs_review, in_progress
    target_category: Mapped[str] = mapped_column(String(50), default="term_life", nullable=False)  # term_life, health, motor
    financial_capacity: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    health_tier: Mapped[str] = mapped_column(String(30), default="standard", nullable=False)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    dependents_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    has_pre_existing_conditions: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    existing_coverage_amount: Mapped[float] = mapped_column(Numeric(14, 2), default=0.00, nullable=False)
    recommended_sum_assured: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    factors_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    completed_steps_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list, nullable=True)

    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="qualifications")
    prospect: Mapped[Optional["Prospect"]] = relationship("Prospect", back_populates="qualifications")


class Recommendation(Base, TimestampMixin):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    recommended_product_id: Mapped[str] = mapped_column(String(36), ForeignKey("insurance_products.id", ondelete="RESTRICT"), nullable=False)
    configuration_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_configurations.id", ondelete="SET NULL"), nullable=True)
    match_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # 0 to 100
    recommended_sum_assured: Mapped[float] = mapped_column(Numeric(14, 2), default=10000000.0, nullable=False)
    recommended_term_years: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    match_factors_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    assumptions_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    limitations_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    alternative_options_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)  # active, accepted, declined

    customer: Mapped["Customer"] = relationship("Customer", back_populates="recommendations")
    conversation: Mapped[Optional["Conversation"]] = relationship("Conversation", back_populates="recommendations")
    recommended_product: Mapped["InsuranceProduct"] = relationship("InsuranceProduct")
    configuration: Mapped[Optional["ProductConfiguration"]] = relationship("ProductConfiguration")


class Quote(Base, TimestampMixin):
    __tablename__ = "quotes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    quote_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("insurance_products.id", ondelete="RESTRICT"), nullable=False, index=True)
    configuration_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("product_configurations.id", ondelete="SET NULL"), nullable=True)
    pricing_matrix_version: Mapped[str] = mapped_column(String(50), default="v1.0.0-actuarial-2026", nullable=False)
    sum_assured: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    policy_term_years: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_frequency: Mapped[str] = mapped_column(String(20), nullable=False)  # monthly, quarterly, half_yearly, annually
    selected_riders_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list, nullable=True)
    base_premium: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    health_loading_amount: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    rider_premium: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    net_premium: Mapped[float] = mapped_column(Numeric(10, 2), default=0.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    total_premium: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    calculation_breakdown_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)  # active, expired, converted

    customer: Mapped["Customer"] = relationship("Customer", back_populates="quotes")
    product: Mapped["InsuranceProduct"] = relationship("InsuranceProduct", back_populates="quotes")
    configuration: Mapped[Optional["ProductConfiguration"]] = relationship("ProductConfiguration")
    application: Mapped[Optional["Application"]] = relationship("Application", back_populates="quote", uselist=False)
