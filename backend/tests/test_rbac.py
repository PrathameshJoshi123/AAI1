"""Automated tests for Role-Based Access Control (RBAC)."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_customer_cannot_access_admin_roles(client: AsyncClient, customer_token: dict):
    resp = await client.get("/api/v1/roles", headers=customer_token)
    assert resp.status_code == 403
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PERMISSION_DENIED"


async def test_customer_cannot_access_underwriting_cases(client: AsyncClient, customer_token: dict):
    resp = await client.get("/api/v1/underwriting/cases", headers=customer_token)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


async def test_advisor_cannot_access_admin_roles(client: AsyncClient, advisor_token: dict):
    resp = await client.get("/api/v1/roles", headers=advisor_token)
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


async def test_advisor_can_access_cases(client: AsyncClient, advisor_token: dict):
    resp = await client.get("/api/v1/underwriting/cases", headers=advisor_token)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_underwriter_can_access_cases(client: AsyncClient, underwriter_token: dict):
    resp = await client.get("/api/v1/underwriting/cases", headers=underwriter_token)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


async def test_admin_can_access_roles_and_audit(client: AsyncClient, admin_token: dict):
    resp_roles = await client.get("/api/v1/roles", headers=admin_token)
    assert resp_roles.status_code == 200
    assert len(resp_roles.json()["data"]) >= 5

    resp_audit = await client.get("/api/v1/audit", headers=admin_token)
    assert resp_audit.status_code == 200
    assert resp_audit.json()["success"] is True

