"""Insurance applications and document vault models."""
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid

if TYPE_CHECKING:
    from app.models.profile import Customer
    from app.models.product import InsuranceProduct
    from app.models.recommendation import Quote
    from app.models.underwriting import UnderwritingCase
    from app.models.auth import User


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    quote_id: Mapped[str] = mapped_column(String(36), ForeignKey("quotes.id", ondelete="RESTRICT"), unique=True, nullable=False, index=True)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("insurance_products.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)  # draft, documents_pending, submitted, under_review, additional_info_required, approved, rejected
    current_step: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    step_progress_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    proposal_data_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    proposal_checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # SHA-256 hash of final proposal_data_json
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="applications")
    quote: Mapped["Quote"] = relationship("Quote", back_populates="application")
    product: Mapped["InsuranceProduct"] = relationship("InsuranceProduct", back_populates="applications")
    documents: Mapped[List["ApplicationDocument"]] = relationship("ApplicationDocument", back_populates="application", cascade="all, delete-orphan")
    underwriting_case: Mapped[Optional["UnderwritingCase"]] = relationship("UnderwritingCase", back_populates="application", uselist=False, cascade="all, delete-orphan")


class ApplicationDocument(Base, TimestampMixin):
    __tablename__ = "application_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # identity_proof, address_proof, income_proof, medical_report, photograph, age_proof
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256 integrity hash
    verification_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)  # pending, extracted, verified, rejected
    extracted_data_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ocr_confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    verified_by_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    application: Mapped["Application"] = relationship("Application", back_populates="documents")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="documents")
    verified_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[verified_by_id])
