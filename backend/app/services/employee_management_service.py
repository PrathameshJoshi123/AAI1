"""Employee Management Service: Staff provisioning, role assignment, and capacity governance."""
import uuid
from typing import List, Optional
from sqlalchemy import func, select, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import utc_now
from app.models.auth import User, Role, UserRole
from app.models.profile import Advisor, Underwriter
from app.models.underwriting import UnderwritingCase
from app.models.audit import AuditLog
from app.core.security import hash_password
from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.schemas.admin import (
    EmployeeCreateRequest,
    EmployeeResponse,
    EmployeeStatusUpdateRequest,
    EmployeeRoleUpdateRequest,
)


class EmployeeManagementService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_employees(self) -> List[EmployeeResponse]:
        """Fetch all users holding internal staff roles (Advisor, Underwriter, Admin, Owner)."""
        # Find all roles that are staff
        query = (
            select(User)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .where(Role.name.in_(["Advisor", "Underwriter", "Admin", "Owner"]))
            .distinct()
            .options(
                selectinload(User.roles),
                selectinload(User.advisor),
                selectinload(User.underwriter),
            )
            .order_by(User.created_at.desc())
        )
        result = await self.session.execute(query)
        users = result.scalars().all()

        responses: List[EmployeeResponse] = []
        for u in users:
            role_names = [r.name for r in u.roles]
            
            # Active caseload for advisor
            active_cases = None
            if u.advisor:
                cnt_res = await self.session.execute(
                    select(func.count(UnderwritingCase.id)).where(
                        UnderwritingCase.assigned_advisor_id == u.advisor.id,
                        UnderwritingCase.status.in_(["new", "under_review", "more_info_required"])
                    )
                )
                active_cases = cnt_res.scalar() or 0

            responses.append(
                EmployeeResponse(
                    id=u.id,
                    email=u.email,
                    first_name=u.first_name,
                    last_name=u.last_name,
                    phone=u.phone,
                    is_active=u.is_active,
                    roles=role_names,
                    created_at=u.created_at,
                    advisor_id=u.advisor.id if u.advisor else None,
                    license_number=u.advisor.license_number if u.advisor else (u.underwriter.license_number if u.underwriter else None),
                    specializations=u.advisor.specializations if u.advisor else None,
                    max_active_cases=u.advisor.max_active_cases if u.advisor else None,
                    active_cases_count=active_cases,
                    is_available=u.advisor.is_available if u.advisor else None,
                    underwriter_id=u.underwriter.id if u.underwriter else None,
                    authority_level=u.underwriter.authority_level if u.underwriter else None,
                    max_coverage_limit=float(u.underwriter.max_coverage_limit) if u.underwriter else None,
                )
            )

        return responses

    async def create_employee(
        self, req: EmployeeCreateRequest, admin_user_id: Optional[str] = None
    ) -> EmployeeResponse:
        """Provision a new employee user account and initialize role-specific profile records."""
        # 1. Check duplicate email
        chk = await self.session.execute(select(User).where(User.email == req.email))
        if chk.scalar_one_or_none():
            raise ConflictException(f"User with email '{req.email}' already exists.")

        # 2. Create User
        hashed_pw = hash_password(req.password)
        new_user = User(
            email=req.email,
            hashed_password=hashed_pw,
            first_name=req.first_name,
            last_name=req.last_name,
            phone=req.phone,
            is_active=True,
            is_verified=True,
        )
        self.session.add(new_user)
        await self.session.flush()

        # 3. Assign Roles
        assigned_role_names: List[str] = []
        for rname in req.role_names:
            role_obj = (
                await self.session.execute(select(Role).where(Role.name == rname))
            ).scalar_one_or_none()
            if role_obj:
                ur = UserRole(user_id=new_user.id, role_id=role_obj.id)
                self.session.add(ur)
                assigned_role_names.append(role_obj.name)

        if not assigned_role_names:
            raise ValidationException("At least one valid staff role must be assigned.")

        # 4. Profile records
        advisor_record = None
        if "Advisor" in assigned_role_names:
            lic = req.license_number or f"ADV-IN-{uuid.uuid4().hex[:6].upper()}"
            advisor_record = Advisor(
                user_id=new_user.id,
                license_number=lic,
                specializations=req.specializations or "Term Life, Health",
                max_active_cases=req.max_active_cases or 50,
                is_available=True,
            )
            self.session.add(advisor_record)

        underwriter_record = None
        if "Underwriter" in assigned_role_names:
            lic = req.license_number or f"UW-IN-{uuid.uuid4().hex[:6].upper()}"
            underwriter_record = Underwriter(
                user_id=new_user.id,
                authority_level=req.authority_level or "Level 1",
                max_coverage_limit=req.max_coverage_limit or 500000.0,
                license_number=lic,
            )
            self.session.add(underwriter_record)

        # 5. Audit log
        audit = AuditLog(
            user_id=admin_user_id,
            action="CREATE_EMPLOYEE",
            resource_type="User",
            resource_id=new_user.id,
            changes_json={
                "email": req.email,
                "roles": assigned_role_names,
                "first_name": req.first_name,
                "last_name": req.last_name,
            },
            timestamp=utc_now(),
        )
        self.session.add(audit)
        await self.session.commit()

        return EmployeeResponse(
            id=new_user.id,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            phone=new_user.phone,
            is_active=new_user.is_active,
            roles=assigned_role_names,
            created_at=new_user.created_at,
            advisor_id=advisor_record.id if advisor_record else None,
            license_number=advisor_record.license_number if advisor_record else (underwriter_record.license_number if underwriter_record else None),
            specializations=advisor_record.specializations if advisor_record else None,
            max_active_cases=advisor_record.max_active_cases if advisor_record else None,
            active_cases_count=0,
            is_available=advisor_record.is_available if advisor_record else None,
            underwriter_id=underwriter_record.id if underwriter_record else None,
            authority_level=underwriter_record.authority_level if underwriter_record else None,
            max_coverage_limit=float(underwriter_record.max_coverage_limit) if underwriter_record else None,
        )

    async def update_employee_status(
        self, user_id: str, req: EmployeeStatusUpdateRequest, admin_user_id: Optional[str] = None
    ) -> None:
        """Toggle active status or advisor availability."""
        u = (await self.session.execute(
            select(User).options(selectinload(User.advisor)).where(User.id == user_id)
        )).scalar_one_or_none()
        if not u:
            raise NotFoundException(f"Employee user '{user_id}' not found.")

        changes = {}
        if req.is_active is not None:
            changes["is_active"] = {"old": u.is_active, "new": req.is_active}
            u.is_active = req.is_active

        if req.is_available is not None and u.advisor:
            changes["is_available"] = {"old": u.advisor.is_available, "new": req.is_available}
            u.advisor.is_available = req.is_available

        audit = AuditLog(
            user_id=admin_user_id,
            action="UPDATE_EMPLOYEE_STATUS",
            resource_type="User",
            resource_id=user_id,
            changes_json=changes,
            timestamp=utc_now(),
        )
        self.session.add(audit)
        await self.session.commit()

    async def update_employee_roles(
        self, user_id: str, req: EmployeeRoleUpdateRequest, admin_user_id: Optional[str] = None
    ) -> None:
        """Update assigned staff roles and create corresponding domain profiles if newly added."""
        u = (await self.session.execute(
            select(User).options(selectinload(User.roles), selectinload(User.advisor), selectinload(User.underwriter)).where(User.id == user_id)
        )).scalar_one_or_none()
        if not u:
            raise NotFoundException(f"Employee user '{user_id}' not found.")

        old_roles = [r.name for r in u.roles]
        
        # Remove old UserRoles
        await self.session.execute(delete(UserRole).where(UserRole.user_id == user_id))

        # Add new UserRoles
        for rname in req.role_names:
            role_obj = (await self.session.execute(select(Role).where(Role.name == rname))).scalar_one_or_none()
            if role_obj:
                ur = UserRole(user_id=user_id, role_id=role_obj.id)
                self.session.add(ur)

        # Ensure profiles exist if role newly added
        if "Advisor" in req.role_names and not u.advisor:
            adv = Advisor(
                user_id=user_id,
                license_number=f"ADV-IN-{uuid.uuid4().hex[:6].upper()}",
                specializations="General Life & Health",
                max_active_cases=50,
                is_available=True,
            )
            self.session.add(adv)

        if "Underwriter" in req.role_names and not u.underwriter:
            uw = Underwriter(
                user_id=user_id,
                authority_level="Level 1",
                max_coverage_limit=500000.0,
                license_number=f"UW-IN-{uuid.uuid4().hex[:6].upper()}",
            )
            self.session.add(uw)

        audit = AuditLog(
            user_id=admin_user_id,
            action="UPDATE_EMPLOYEE_ROLES",
            resource_type="User",
            resource_id=user_id,
            changes_json={"old_roles": old_roles, "new_roles": req.role_names},
            timestamp=utc_now(),
        )
        self.session.add(audit)
        await self.session.commit()

