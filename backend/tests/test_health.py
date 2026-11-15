"""Automated tests for Health and System Readiness."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_health_check(client: AsyncClient):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


async def test_database_health_check(client: AsyncClient):
    resp = await client.get("/api/v1/health/db")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["database"] == "sqlite"
    assert body["data"]["connection"] == "ok"


async def test_products_list(client: AsyncClient):
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert len(body["data"]) >= 2

