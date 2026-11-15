"""Roles and Permissions Management Endpoints."""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, require_roles
from app.models.auth import Permission, Role, User
from app.schemas.auth import PermissionRead, RoleRead
from app.schemas.common import APIResponse

router = APIRouter(prefix="/roles", tags=["Roles & RBAC"])


@router.get("", response_model=APIResponse[List[RoleRead]])
async def list_roles(
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve all roles and their granted permissions (Admin / Owner only)."""
    stmt = select(Role).options(selectinload(Role.permissions))
    result = await session.execute(stmt)
    roles = result.scalars().all()
    return APIResponse(
        data=[RoleRead.model_validate(r) for r in roles]
    )


@router.get("/permissions", response_model=APIResponse[List[PermissionRead]])
async def list_permissions(
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
    session: AsyncSession = Depends(get_db),
):
    """Retrieve all granular permissions in the platform (Admin / Owner only)."""
    stmt = select(Permission)
    result = await session.execute(stmt)
    perms = result.scalars().all()
    return APIResponse(
        data=[PermissionRead.model_validate(p) for p in perms]
    )

