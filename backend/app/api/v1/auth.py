"""Authentication & Identity Endpoints."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_current_user_token, get_db
from app.models.auth import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRead,
    UserRegisterRequest,
)
from app.schemas.common import APIResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[UserRead], status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegisterRequest,
    session: AsyncSession = Depends(get_db),
):
    """Register a new user account with initial role and profile."""
    auth_service = AuthService(session)
    user = await auth_service.register(data)
    return APIResponse(
        data=UserRead.model_validate(user),
        message="User account created successfully.",
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login(
    data: LoginRequest,
    session: AsyncSession = Depends(get_db),
):
    """Authenticate email and password to receive JWT access and refresh tokens."""
    auth_service = AuthService(session)
    tokens = await auth_service.login(data)
    return APIResponse(
        data=tokens,
        message="Authentication successful.",
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_tokens(
    data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db),
):
    """Rotate an existing refresh token for a new access & refresh token pair."""
    auth_service = AuthService(session)
    tokens = await auth_service.refresh_tokens(data.refresh_token)
    return APIResponse(
        data=tokens,
        message="Token refreshed successfully.",
    )


@router.post("/logout", response_model=APIResponse[dict])
async def logout(
    payload: Dict[str, Any] = Depends(get_current_user_token),
    session: AsyncSession = Depends(get_db),
):
    """Revoke the current session token."""
    auth_service = AuthService(session)
    await auth_service.logout(payload)
    return APIResponse(
        data={"revoked": True},
        message="Successfully logged out.",
    )


@router.get("/me", response_model=APIResponse[UserRead])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Retrieve full profile, roles, and permissions of the currently authenticated user."""
    return APIResponse(
        data=UserRead.model_validate(current_user),
    )

