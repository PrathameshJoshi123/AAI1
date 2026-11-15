"""FastAPI Dependencies for Authentication, RBAC, and Tenant Data Scoping."""
from typing import Any, Callable, Dict, List, Optional
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import AuthenticationFailedException, PermissionDeniedException
from app.core.security import decode_token
from app.models.auth import User
from app.repositories.user_repository import AuthRepository, UserRepository

security = HTTPBearer(auto_error=False)


async def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> Dict[str, Any]:
    """Extract and cryptographically decode the JWT Bearer token payload."""
    if not credentials or not credentials.credentials:
        raise AuthenticationFailedException("Authentication credentials are required.")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise AuthenticationFailedException("Invalid, malformed, or expired access token.")

    if payload.get("type") != "access":
        raise AuthenticationFailedException("Invalid token type. Access token required.")

    return payload


async def get_current_user(
    payload: Dict[str, Any] = Depends(get_current_user_token),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Verify token revocation status and return the active User entity."""
    jti = payload.get("jti")
    auth_repo = AuthRepository(session)
    if not jti or await auth_repo.is_token_revoked(jti):
        raise AuthenticationFailedException("Session has been revoked or logged out.")

    user_id = payload.get("sub")
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id_with_details(user_id)

    if not user:
        raise AuthenticationFailedException("User not found.")

    if not user.is_active:
        raise AuthenticationFailedException("User account is inactive.")

    return user


def require_roles(allowed_roles: List[str]) -> Callable:
    """Role-Based Access Control (RBAC) dependency factory."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = [role.name for role in current_user.roles]
        # Superusers (Owner) always have access
        if "Owner" in user_role_names:
            return current_user

        if not any(role in allowed_roles for role in user_role_names):
            raise PermissionDeniedException(
                f"Access denied: Required role in {allowed_roles}, your roles: {user_role_names}"
            )
        return current_user

    return role_checker


def require_permission(required_permission_code: str) -> Callable:
    """Fine-grained Permission-Based Authorization dependency factory."""
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_names = [role.name for role in current_user.roles]
        if "Owner" in user_role_names:
            return current_user

        user_permissions = {
            perm.code
            for role in current_user.roles
            for perm in role.permissions
        }

        if required_permission_code not in user_permissions:
            raise PermissionDeniedException(
                f"Access denied: Required permission '{required_permission_code}' is missing."
            )
        return current_user

    return permission_checker


async def get_scoped_customer_id(
    target_customer_id: str,
    current_user: User = Depends(get_current_user),
) -> str:
    """Ensure strict customer data isolation: customers can only access their own records."""
    user_roles = [r.name for r in current_user.roles]

    # Admin, Underwriter, Owner have management access
    if any(r in ("Admin", "Owner", "Underwriter") for r in user_roles):
        return target_customer_id

    # Advisors can access if assigned
    if "Advisor" in user_roles and current_user.advisor:
        return target_customer_id

    # Customer role is strictly bounded to their own customer ID
    if "Customer" in user_roles:
        if not current_user.customer or current_user.customer.id != target_customer_id:
            raise PermissionDeniedException("Access denied: You cannot view or modify another customer's data.")
        return target_customer_id

    raise PermissionDeniedException("Access denied: Insufficient scope.")


async def get_current_customer(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve active Customer entity associated with current authenticated user."""
    from app.models.profile import Customer
    from sqlalchemy import select
    stmt = select(Customer).where(Customer.user_id == current_user.id)
    res = await session.execute(stmt)
    customer = res.scalar_one_or_none()
    if not customer:
        customer = Customer(user_id=current_user.id)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
    return customer


