"""Tests for Deterministic Lead Scoring and Explainable Factors."""
import pytest


@pytest.mark.asyncio
async def test_deterministic_scoring_accumulation(client, admin_auth):
    # 1. Ingest prospect with Phone (+15), Email (+10), Name (+5) -> Base 30
    payload = {
        "name": "Amit Shah",
        "email": "amit.s@example.com",
        "phone": "+919988776655",
        "initial_session_id": "sess-amit-1",
    }
    resp = await client.post("/api/v1/prospects", json=payload)
    assert resp.status_code == 201
    prospect_id = resp.json()["data"]["id"]
    assert resp.json()["data"]["latest_score"] == 30.0

    # 2. Ingest Quote Attempt Signal (+25)
    sig_resp = await client.post(
        "/api/v1/signals",
        json={
            "session_id": "sess-amit-1",
            "prospect_id": prospect_id,
            "signal_type": "quote_attempt",
            "payload_json": {"product_name": "Term Life 1Cr"},
        },
    )
    assert sig_resp.status_code == 201

    # 3. Ingest Dwell Time Signal (+10)
    await client.post(
        "/api/v1/signals",
        json={
            "session_id": "sess-amit-1",
            "prospect_id": prospect_id,
            "signal_type": "time_on_page",
            "payload_json": {"duration_seconds": 150, "path": "/products/term-life"},
        },
    )

    # 4. Ingest Marketing Consent (+10)
    await client.post(
        "/api/v1/consent",
        json={
            "prospect_id": prospect_id,
            "consent_type": "marketing_contact",
            "consent_version": "2026.1",
            "ip_address": "127.0.0.1",
        },
    )

    # Total Expected Score = 15 (Phone) + 10 (Email) + 5 (Name) + 25 (Quote) + 10 (Dwell) + 10 (Consent) = 75.0
    detail_resp = await client.get(f"/api/v1/prospects/{prospect_id}", headers=admin_auth)
    assert detail_resp.status_code == 200
    detail = detail_resp.json()["data"]

    latest_score = detail["latest_score"]
    assert latest_score["score"] == 75.0
    assert detail["segment"] == "high_intent"
    assert detail["can_contact"] is True

    # Verify explainable factors breakdown
    factors = latest_score["factors"]
    assert len(factors) == 6
    factor_codes = [f["rule_code"] for f in factors]
    assert "RULE_PROFILE_PHONE" in factor_codes
    assert "RULE_INTENT_QUOTE_STARTED" in factor_codes
    assert "RULE_CONSENT_MARKETING" in factor_codes

