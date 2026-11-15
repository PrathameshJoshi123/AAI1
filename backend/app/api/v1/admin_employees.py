"""Admin Employee Management API Router."""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import require_roles
from app.core.database import get_db
from app.models.auth import User
from app.schemas.admin import (
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeStatusUpdateRequest,
    EmployeeRoleUpdateRequest,
)
from app.services.employee_management_service import EmployeeManagementService

router = APIRouter(prefix="/admin/employees", tags=["Admin - Employee Management"])


@router.get("", response_model=List[EmployeeResponse])
async def list_employees(
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> List[EmployeeResponse]:
    """List all internal staff members across advisor, underwriter, and admin roles."""
    service = EmployeeManagementService(session)
    return await service.list_employees()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    req: EmployeeCreateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> EmployeeResponse:
    """Provision a new employee user account and assign roles/credentials."""
    service = EmployeeManagementService(session)
    return await service.create_employee(req, admin_user_id=current_user.id)


@router.patch("/{user_id}/status", status_code=status.HTTP_200_OK)
async def update_employee_status(
    user_id: str,
    req: EmployeeStatusUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> dict:
    """Update employee active status or advisor availability."""
    service = EmployeeManagementService(session)
    await service.update_employee_status(user_id, req, admin_user_id=current_user.id)
    return {"status": "success", "message": "Employee status updated successfully."}


@router.put("/{user_id}/roles", status_code=status.HTTP_200_OK)
async def update_employee_roles(
    user_id: str,
    req: EmployeeRoleUpdateRequest,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["Admin", "Owner"])),
) -> dict:
    """Update employee assigned roles and synchronize profile capabilities."""
    service = EmployeeManagementService(session)
    await service.update_employee_roles(user_id, req, admin_user_id=current_user.id)
    return {"status": "success", "message": "Employee roles updated successfully."}

