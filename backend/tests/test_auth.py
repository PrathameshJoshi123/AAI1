"""Automated tests for Authentication and Token Lifecycle."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_register_new_customer(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newcustomer@example.com",
            "password": "SecurePassword123!",
            "first_name": "Jane",
            "last_name": "Doe",
            "phone": "+1234567890",
            "role": "Customer",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["email"] == "newcustomer@example.com"
    assert len(body["data"]["roles"]) > 0
    assert body["data"]["roles"][0]["name"] == "Customer"


async def test_login_success(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ps21-insurance.com", "password": "AdminPass123!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["user"]["email"] == "admin@ps21-insurance.com"


async def test_login_invalid_password(client: AsyncClient):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ps21-insurance.com", "password": "WrongPassword!"},
    )
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "AUTHENTICATION_FAILED"


async def test_refresh_token_rotation(client: AsyncClient):
    # 1. Login to get initial tokens
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ps21-insurance.com", "password": "AdminPass123!"},
    )
    initial_refresh = login_resp.json()["data"]["refresh_token"]

    # 2. Refresh tokens
    refresh_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert refresh_resp.status_code == 200
    body = refresh_resp.json()
    assert body["success"] is True
    new_refresh = body["data"]["refresh_token"]
    assert new_refresh != initial_refresh

    # 3. Old refresh token must be revoked and rejected
    reused_resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert reused_resp.status_code == 401
    assert reused_resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"


async def test_logout_revokes_token(client: AsyncClient):
    # 1. Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@ps21-insurance.com", "password": "AdminPass123!"},
    )
    token = login_resp.json()["data"]["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    # 2. Access /me works
    me_resp = await client.get("/api/v1/auth/me", headers=auth_header)
    assert me_resp.status_code == 200

    # 3. Logout
    logout_resp = await client.post("/api/v1/auth/logout", headers=auth_header)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["data"]["revoked"] is True

    # 4. Subsequent request with revoked token must fail with 401
    me_revoked_resp = await client.get("/api/v1/auth/me", headers=auth_header)
    assert me_revoked_resp.status_code == 401
    assert me_revoked_resp.json()["error"]["code"] == "AUTHENTICATION_FAILED"

