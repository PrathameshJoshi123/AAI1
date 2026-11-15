"""Pydantic schemas for Authentication and Authorization."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class PermissionRead(BaseModel):
    id: int
    code: str
    description: Optional[str] = None
    module: str

    model_config = {"from_attributes": True}


class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionRead] = []

    model_config = {"from_attributes": True}


class UserRead(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    roles: List[RoleRead] = []

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    role: str = Field(default="Customer", pattern="^(Customer|Advisor|Underwriter|Admin|Owner)$")

