"""Customer Profile and Preferences Schemas."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class CustomerProfileRead(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    marital_status: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    health_status: Optional[str] = None
    risk_tier: str = "standard"
    preferred_language: str = "en"
    city: Optional[str] = None
    pincode: Optional[str] = None
    state: Optional[str] = None
    gender: Optional[str] = None
    tobacco_user: bool = False
    onboarding_stage: str = "discovery"
    active_conversation_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CustomerProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    date_of_birth: Optional[date] = None
    marital_status: Optional[str] = Field(None, pattern=r"^(single|married|divorced|widowed)$")
    occupation: Optional[str] = Field(None, max_length=100)
    annual_income: Optional[float] = Field(None, ge=0)
    gender: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    city: Optional[str] = Field(None, max_length=100)
    pincode: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=50)
    tobacco_user: Optional[bool] = None
    preferred_language: Optional[str] = Field(None, pattern=r"^(en|hi)$")

