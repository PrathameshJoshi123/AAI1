"""Authentication and Authorization Business Service."""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import (
    AuthenticationFailedException,
    BusinessRuleViolationException,
    EntityNotFoundException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.auth import RevokedToken, User
from app.models.profile import Customer, Advisor, Underwriter
from app.repositories.user_repository import AuthRepository, UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserRead, UserRegisterRequest


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.auth_repo = AuthRepository(session)

    async def register(self, data: UserRegisterRequest) -> User:
        """Register a new user and create their corresponding domain profile."""
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise BusinessRuleViolationException(f"User with email '{data.email}' already exists.")

        role = await self.user_repo.get_role_by_name(data.role)
        if not role:
            raise EntityNotFoundException(f"Role '{data.role}' not found in system.")

        user = User(
            email=data.email.lower().strip(),
            hashed_password=hash_password(data.password),
            first_name=data.first_name,
            last_name=data.last_name,
            phone=data.phone,
            is_active=True,
            is_verified=False,
        )
        created_user = await self.user_repo.create(user)

        # Assign Role
        await self.user_repo.assign_role_to_user(created_user.id, role.id)

        # Create Domain Profile based on role
        if data.role == "Customer":
            customer = Customer(user_id=created_user.id)
            self.session.add(customer)
        elif data.role == "Advisor":
            advisor = Advisor(
                user_id=created_user.id,
                license_number=f"ADV-{created_user.id[:8].upper()}",
            )
            self.session.add(advisor)
        elif data.role == "Underwriter":
            underwriter = Underwriter(
                user_id=created_user.id,
                license_number=f"UW-{created_user.id[:8].upper()}",
            )
            self.session.add(underwriter)

        await self.session.flush()
        # Reload with relationships
        return await self.user_repo.get_by_id_with_details(created_user.id)  # type: ignore

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user credentials and issue signed token pair."""
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise AuthenticationFailedException("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailedException("User account is inactive. Please contact administrator.")

        role_names = [r.name for r in user.roles]
        access_token = create_access_token(
            subject=user.id,
            email=user.email,
            roles=role_names,
        )
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=15 * 60,
            user=UserRead.model_validate(user),
        )

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse:
        """Validate refresh token, revoke it, and issue a fresh rotated token pair."""
        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            raise AuthenticationFailedException("Invalid or expired refresh token.")

        if payload.get("type") != "refresh":
            raise AuthenticationFailedException("Invalid token type. Refresh token required.")

        jti = payload.get("jti")
        if not jti or await self.auth_repo.is_token_revoked(jti):
            raise AuthenticationFailedException("Refresh token has been revoked or is invalid.")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id_with_details(user_id)
        if not user or not user.is_active:
            raise AuthenticationFailedException("User not found or inactive.")

        # Revoke the used refresh token (Token Rotation)
        exp_timestamp = payload.get("exp", int(datetime.now(timezone.utc).timestamp()))
        revoked_token = RevokedToken(
            jti=jti,
            user_id=user.id,
            token_type="refresh",
            expires_at=datetime.fromtimestamp(exp_timestamp, tz=timezone.utc),
            reason="rotation",
        )
        await self.auth_repo.revoke_token(revoked_token)

        # Issue new pair
        role_names = [r.name for r in user.roles]
        new_access_token = create_access_token(
            subject=user.id,
            email=user.email,
            roles=role_names,
        )
        new_refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=15 * 60,
            user=UserRead.model_validate(user),
        )

    async def logout(self, token_payload: dict, reason: str = "logout") -> None:
        """Revoke the current access token."""
        jti = token_payload.get("jti")
        user_id = token_payload.get("sub")
        exp = token_payload.get("exp")
        token_type = token_payload.get("type", "access")

        if jti and user_id and exp:
            revoked_token = RevokedToken(
                jti=jti,
                user_id=user_id,
                token_type=token_type,
                expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
                reason=reason,
            )
            await self.auth_repo.revoke_token(revoked_token)

