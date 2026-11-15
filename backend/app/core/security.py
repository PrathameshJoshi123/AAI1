"""Security, cryptography, and token utilities."""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import uuid
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

# Initialize password hash engine (Argon2 / Bcrypt)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password using recommended cryptographic salt hashing."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored cryptographic hash."""
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    email: str,
    roles: List[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token with user claims."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "email": email,
        "roles": roles,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT refresh token."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode and cryptographically verify a JWT token."""
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise

