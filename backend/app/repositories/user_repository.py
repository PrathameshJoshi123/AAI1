"""Repository for User and RBAC queries."""
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth import User, Role, Permission, UserRole, RevokedToken
from app.models.profile import Customer, Advisor, Underwriter
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.email == email.lower().strip())
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.customer),
                selectinload(User.advisor),
                selectinload(User.underwriter),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_details(self, user_id: str) -> Optional[User]:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.roles).selectinload(Role.permissions),
                selectinload(User.customer),
                selectinload(User.advisor),
                selectinload(User.underwriter),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        stmt = select(Role).where(Role.name == name).options(selectinload(Role.permissions))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def assign_role_to_user(self, user_id: str, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(user_role)
        await self.session.flush()
        return user_role


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_token_revoked(self, jti: str) -> bool:
        stmt = select(RevokedToken).where(RevokedToken.jti == jti)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def revoke_token(self, revoked_token: RevokedToken) -> RevokedToken:
        self.session.add(revoked_token)
        await self.session.flush()
        return revoked_token

