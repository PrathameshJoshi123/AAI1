"""Insurance products and policy configuration catalog models."""
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.recommendation import Quote
    from app.models.application import Application
    from app.models.pricing_matrix import ProductPricingMatrix


class InsuranceProduct(Base, TimestampMixin):
    __tablename__ = "insurance_products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # term_life, health, disability, critical_illness
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    base_rules_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    # Insurer profile & regulatory details
    insurer_name: Mapped[str] = mapped_column(String(150), default="Star Union Life & General", nullable=False)
    insurer_code: Mapped[str] = mapped_column(String(50), default="SULG-IN", nullable=False)
    insurer_solvency_ratio: Mapped[float] = mapped_column(Numeric(5, 2), default=2.15, nullable=False)
    policy_type: Mapped[str] = mapped_column(String(50), default="individual", nullable=False)  # individual, family_floater, group

    # Structured policy underwriting and compliance metadata
    coverage_summary_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    benefits_list_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    exclusions_list_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    waiting_periods_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    required_declarations_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    required_documents_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    # Relationships
    configurations: Mapped[List["ProductConfiguration"]] = relationship(
        "ProductConfiguration", back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    pricing_matrices: Mapped[List["ProductPricingMatrix"]] = relationship(
        "ProductPricingMatrix", back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )
    quotes: Mapped[List["Quote"]] = relationship("Quote", back_populates="product")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="product")


class ProductConfiguration(Base, TimestampMixin):
    __tablename__ = "product_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("insurance_products.id", ondelete="CASCADE"), nullable=False, index=True)
    tier_name: Mapped[str] = mapped_column(String(50), nullable=False)  # Essential, Comprehensive, Elite
    min_sum_assured: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    max_sum_assured: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    sum_assured_step: Mapped[float] = mapped_column(Numeric(14, 2), default=500000.0, nullable=False)
    term_options_json: Mapped[Optional[List[int]]] = mapped_column(JSON, nullable=True)  # [10, 15, 20, 25, 30]
    available_frequencies_json: Mapped[Optional[List[str]]] = mapped_column(JSON, default=lambda: ["monthly", "quarterly", "annually"], nullable=True)
    riders_json: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)

    product: Mapped["InsuranceProduct"] = relationship("InsuranceProduct", back_populates="configurations")
