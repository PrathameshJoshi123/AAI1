"""Actuarial pricing matrices for deterministic insurance premium calculation."""
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.product import InsuranceProduct


class ProductPricingMatrix(Base, TimestampMixin):
    __tablename__ = "product_pricing_matrices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("insurance_products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    matrix_version: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Actuarial pricing tables and factor matrices
    age_band_rates_json: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    gender_multipliers_json: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    smoker_loading_factors_json: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    frequency_multipliers_json: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    health_tier_loadings_json: Mapped[Dict[str, float]] = mapped_column(JSON, nullable=False)
    rider_rate_cards_json: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    tax_rate_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=18.00, nullable=False)

    # Relationship
    product: Mapped["InsuranceProduct"] = relationship("InsuranceProduct", back_populates="pricing_matrices")

