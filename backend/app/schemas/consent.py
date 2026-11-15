"""Pydantic schemas for Legal Consent Management (DPDP & IRDAI)."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ConsentGrantRequest(BaseModel):
    prospect_id: str
    consent_type: str = Field(
        ...,
        pattern=r"^(terms_of_service|privacy_policy|marketing_contact|quote_generation|medical_record_access)$"
    )
    consent_version: str = Field("2026.1", max_length=20)
    ip_address: Optional[str] = Field(None, max_length=45)


class ConsentRevokeRequest(BaseModel):
    prospect_id: str
    consent_type: str = Field(
        ...,
        pattern=r"^(terms_of_service|privacy_policy|marketing_contact|quote_generation|medical_record_access)$"
    )
    reason: Optional[str] = Field(None, max_length=255)


class ConsentRecordRead(BaseModel):
    id: int
    consent_type: str
    consent_version: str
    ip_address: Optional[str] = None
    granted_at: datetime
    revoked_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ConsentStatusResponse(BaseModel):
    prospect_id: str
    can_contact: bool
    active_consents: List[str] = Field(default_factory=list)

