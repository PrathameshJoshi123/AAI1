"""Pydantic schemas for Document Vault and Verification."""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class DocumentRequirementItem(BaseModel):
    document_type: str = Field(..., description="e.g. identity_proof, address_proof, income_proof, medical_report")
    title: str
    description: Optional[str] = None
    mandatory: bool = True
    accepted_mime_types: List[str] = Field(default_factory=lambda: ["application/pdf", "image/jpeg", "image/png"])
    condition_description: Optional[str] = None


class DocumentRead(BaseModel):
    id: str
    application_id: str
    customer_id: str
    document_type: str
    version: int
    file_name: str
    file_size_bytes: int
    mime_type: str
    file_hash: str
    verification_status: str  # pending, extracted, verified, rejected
    extracted_data_json: Optional[Dict[str, Any]] = None
    ocr_confidence_score: Optional[float] = None
    verified_by_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    message: str = "Document uploaded successfully and integrity verified."


class DocumentVerifyRequest(BaseModel):
    decision: Literal["verified", "rejected"]
    rejection_reason: Optional[str] = None
