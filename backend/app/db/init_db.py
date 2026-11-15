"""Seed core roles, granular permissions, and initial administrator user."""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.auth import Permission, Role, RolePermission, User, UserRole


ROLES_CONFIG = [
    {"name": "Customer", "description": "Retail customer evaluating and applying for insurance."},
    {"name": "Advisor", "description": "Licensed insurance agent managing assigned customer pipelines."},
    {"name": "Underwriter", "description": "Risk specialist evaluating medical/financial proposals."},
    {"name": "Admin", "description": "Operations administrator managing users, products, and rules."},
    {"name": "Owner", "description": "Platform superuser with unrestricted operational authority."},
]

PERMISSIONS_CONFIG = [
    # Customer
    {"code": "profile:read", "description": "Read own profile", "module": "auth"},
    {"code": "profile:update", "description": "Update own profile", "module": "auth"},
    {"code": "quotes:create", "description": "Generate an indicative quote", "module": "quotes"},
    {"code": "quotes:read_own", "description": "View own quotes", "module": "quotes"},
    {"code": "applications:create", "description": "Submit a proposal application", "module": "applications"},
    {"code": "applications:read_own", "description": "View own applications", "module": "applications"},
    # Advisor
    {"code": "cases:read_assigned", "description": "Read cases assigned to advisor", "module": "cases"},
    {"code": "leads:manage", "description": "Manage assigned prospect leads", "module": "prospects"},
    # Underwriter
    {"code": "cases:read_all", "description": "View all underwriting cases", "module": "underwriting"},
    {"code": "cases:review", "description": "Submit review decision on case", "module": "underwriting"},
    {"code": "medical_data:view", "description": "Inspect sensitive medical health records", "module": "underwriting"},
    {"code": "financial_data:view", "description": "Inspect sensitive tax and income records", "module": "underwriting"},
    # Admin & Owner
    {"code": "users:manage", "description": "Manage user accounts and role assignments", "module": "admin"},
    {"code": "pricing:manage", "description": "Configure products and pricing logic", "module": "admin"},
    {"code": "audit:read", "description": "Inspect security and compliance audit logs", "module": "audit"},
    {"code": "settings:manage", "description": "Update dynamic system settings", "module": "admin"},
]

ROLE_PERMISSION_MAP = {
    "Customer": ["profile:read", "profile:update", "quotes:create", "quotes:read_own", "applications:create", "applications:read_own"],
    "Advisor": ["profile:read", "profile:update", "quotes:create", "quotes:read_own", "applications:create", "applications:read_own", "cases:read_assigned", "leads:manage"],
    "Underwriter": ["profile:read", "cases:read_all", "cases:review", "medical_data:view", "financial_data:view"],
    "Admin": ["profile:read", "cases:read_all", "cases:review", "medical_data:view", "financial_data:view", "users:manage", "pricing:manage", "audit:read", "settings:manage"],
    "Owner": [p["code"] for p in PERMISSIONS_CONFIG],
}


async def seed_roles_and_permissions(session):
    # 1. Seed Permissions
    perm_dict = {}
    for p_data in PERMISSIONS_CONFIG:
        stmt = select(Permission).where(Permission.code == p_data["code"])
        result = await session.execute(stmt)
        perm = result.scalar_one_or_none()
        if not perm:
            perm = Permission(**p_data)
            session.add(perm)
            await session.flush()
        perm_dict[perm.code] = perm

    # 2. Seed Roles
    role_dict = {}
    for r_data in ROLES_CONFIG:
        stmt = select(Role).where(Role.name == r_data["name"])
        result = await session.execute(stmt)
        role = result.scalar_one_or_none()
        if not role:
            role = Role(**r_data)
            session.add(role)
            await session.flush()
        role_dict[role.name] = role

    # 3. Link Role Permissions
    for role_name, perm_codes in ROLE_PERMISSION_MAP.items():
        role = role_dict[role_name]
        for p_code in perm_codes:
            perm = perm_dict[p_code]
            stmt = select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id,
            )
            result = await session.execute(stmt)
            if not result.scalar_one_or_none():
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))
    await session.flush()

    # 4. Seed Default Admin User
    admin_email = "admin@ps21-insurance.com"
    stmt = select(User).where(User.email == admin_email)
    result = await session.execute(stmt)
    admin_user = result.scalar_one_or_none()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            hashed_password=hash_password("AdminPass123!"),
            first_name="Platform",
            last_name="Administrator",
            is_active=True,
            is_verified=True,
        )
        session.add(admin_user)
        await session.flush()

        # Assign Admin and Owner roles
        session.add(UserRole(user_id=admin_user.id, role_id=role_dict["Admin"].id))
        session.add(UserRole(user_id=admin_user.id, role_id=role_dict["Owner"].id))
        await session.flush()
        print(f"Default admin user created: {admin_email}")
    else:
        print(f"Admin user {admin_email} already exists.")


async def main():
    async with AsyncSessionLocal() as session:
        try:
            await seed_roles_and_permissions(session)
            await session.commit()
            print("Roles, permissions, and admin user initialized successfully!")
        except Exception as e:
            await session.rollback()
            print(f"Error during init_db: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())

