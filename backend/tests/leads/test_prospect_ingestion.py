"""Tests for Prospect Ingestion and Attribution."""
import pytest


@pytest.mark.asyncio
async def test_ingest_prospect_with_utm_attribution(client):
    payload = {
        "name": "Rajesh Kumar",
        "email": "rajesh.k@example.com",
        "phone": "+919876543210",
        "source_name": "google_ads",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "term_life_q4",
        "target_insurance_type": "term_life",
        "initial_session_id": "sess-utm-101",
    }
    resp = await client.post("/api/v1/prospects", json=payload)
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["name"] == "Rajesh Kumar"
    assert data["email"] == "rajesh.k@example.com"
    assert data["phone"] == "+919876543210"
    assert data["target_insurance_type"] == "term_life"
    assert data["status"] in ("new", "engaged", "qualified")
    # Score should include Phone (15) + Email (10) + Name (5) = 30
    assert data["latest_score"] == 30.0


@pytest.mark.asyncio
async def test_ingest_prospect_deduplication(client):
    # First ingestion with email
    payload1 = {
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "initial_session_id": "sess-priya-1",
    }
    resp1 = await client.post("/api/v1/prospects", json=payload1)
    assert resp1.status_code == 201
    prospect_id_1 = resp1.json()["data"]["id"]

    # Second ingestion with same email and newly provided phone
    payload2 = {
        "email": "priya.sharma@example.com",
        "phone": "+919811122233",
        "initial_session_id": "sess-priya-2",
    }
    resp2 = await client.post("/api/v1/prospects", json=payload2)
    assert resp2.status_code == 201
    prospect_id_2 = resp2.json()["data"]["id"]

    # Deduplicated to same prospect record
    assert prospect_id_1 == prospect_id_2
    assert resp2.json()["data"]["phone"] == "+919811122233"

