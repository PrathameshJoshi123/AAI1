"""Pytest configuration, fixtures, and authenticated test clients."""
import asyncio
import os
import sys
from typing import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.api.deps import get_db
from app.core.config import settings
from app.models.base import Base
from app.db.init_db import seed_roles_and_permissions
from app.db.seed_products import seed_products
from app.db.seed_leads import DEFAULT_LEAD_SOURCES, DEFAULT_SCORING_RULES
from app.models.prospect import LeadScoringRule, LeadSource
from app.main import app
from app.models.auth import Role, User, UserRole
from app.models.profile import Customer, Advisor, Underwriter
from app.core.security import hash_password

# Test database
TEST_DB_FILE = "test_ps21.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///./{TEST_DB_FILE}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="function")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Create test database schema and seed essential roles, permissions, and products."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        await seed_roles_and_permissions(session)
        await seed_products(session)
        for s in DEFAULT_LEAD_SOURCES:
            session.add(LeadSource(**s))
        for r in DEFAULT_SCORING_RULES:
            session.add(LeadScoringRule(**r))
        await session.commit()

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()

    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def create_user_with_role(email: str, password: str, role_name: str, first: str = "Test", last: str = "User"):
    async with TestSessionLocal() as session:
        from sqlalchemy import select
        # Check existing
        stmt = select(User).where(User.email == email)
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            return existing

        role_res = await session.execute(select(Role).where(Role.name == role_name))
        role = role_res.scalar_one()

        user = User(
            email=email,
            hashed_password=hash_password(password),
            first_name=first,
            last_name=last,
            is_active=True,
            is_verified=True,
        )
        session.add(user)
        await session.flush()
        session.add(UserRole(user_id=user.id, role_id=role.id))

        if role_name == "Customer":
            session.add(Customer(user_id=user.id))
        elif role_name == "Advisor":
            session.add(Advisor(user_id=user.id, license_number=f"ADV-{user.id[:8]}"))
        elif role_name == "Underwriter":
            session.add(Underwriter(user_id=user.id, license_number=f"UW-{user.id[:8]}"))

        await session.commit()
        return user


@pytest.fixture
async def customer_token(client: AsyncClient) -> dict:
    await create_user_with_role("customer_a@example.com", "Password123!", "Customer", "Alice", "Customer")
    resp = await client.post("/api/v1/auth/login", json={"email": "customer_a@example.com", "password": "Password123!"})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def customer_b_token(client: AsyncClient) -> dict:
    await create_user_with_role("customer_b@example.com", "Password123!", "Customer", "Bob", "Customer")
    resp = await client.post("/api/v1/auth/login", json={"email": "customer_b@example.com", "password": "Password123!"})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def advisor_token(client: AsyncClient) -> dict:
    await create_user_with_role("advisor@example.com", "Password123!", "Advisor", "Dan", "Advisor")
    resp = await client.post("/api/v1/auth/login", json={"email": "advisor@example.com", "password": "Password123!"})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def underwriter_token(client: AsyncClient) -> dict:
    await create_user_with_role("underwriter@example.com", "Password123!", "Underwriter", "Ursula", "Underwriter")
    resp = await client.post("/api/v1/auth/login", json={"email": "underwriter@example.com", "password": "Password123!"})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def admin_token(client: AsyncClient) -> dict:
    resp = await client.post("/api/v1/auth/login", json={"email": "admin@ps21-insurance.com", "password": "AdminPass123!"})
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
