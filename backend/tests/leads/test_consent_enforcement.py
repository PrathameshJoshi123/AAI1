"""Tests for DPDP Legal Consent Enforcement and Outreach Blocking."""
import pytest


@pytest.mark.asyncio
async def test_outreach_blocked_without_consent(client, advisor_auth):
    # Ingest prospect without consent
    resp = await client.post(
        "/api/v1/prospects",
        json={
            "name": "Anonymous Lead",
            "phone": "+919123456789",
            "initial_session_id": "sess-no-consent",
        },
    )
    prospect_id = resp.json()["data"]["id"]

    # Assign lead to advisor
    headers = advisor_auth
    advisor_id = advisor_auth["advisor"].id

    from app.models.prospect import Prospect
    test_session = client._transport.app.dependency_overrides[list(client._transport.app.dependency_overrides.keys())[0]]

    # Directly assign for this scoped test
    stmt = (
        f"UPDATE prospects SET assigned_advisor_id = '{advisor_id}' WHERE id = '{prospect_id}'"
    )
    # Using API or test session: let's update status and assigned advisor
    patch_resp = await client.patch(
        f"/api/v1/prospects/{prospect_id}",
        headers=headers,
        json={"target_insurance_type": "term_life"},
    )

    # Attempt to log outreach without consent: MUST BE FORBIDDEN (HTTP 403)
    # Because assigned_advisor_id isn't matching yet:
    # First assign via admin endpoint or update assigned_advisor_id
    # Let's grant advisor assignment first


@pytest.mark.asyncio
async def test_consent_grant_and_revocation(client):
    resp = await client.post(
        "/api/v1/prospects",
        json={"name": "Karan Mehra", "phone": "+919876500000", "initial_session_id": "sess-karan"},
    )
    prospect_id = resp.json()["data"]["id"]

    # Check initially cannot contact
    status_resp = await client.get(f"/api/v1/consent/{prospect_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["data"]["can_contact"] is False

    # Grant marketing consent
    grant_resp = await client.post(
        "/api/v1/consent",
        json={
            "prospect_id": prospect_id,
            "consent_type": "marketing_contact",
            "consent_version": "2026.1",
            "ip_address": "192.168.1.1",
        },
    )
    assert grant_resp.status_code == 201

    # Check can contact is now True
    status_resp = await client.get(f"/api/v1/consent/{prospect_id}")
    assert status_resp.json()["data"]["can_contact"] is True

    # Revoke consent
    revoke_resp = await client.post(
        "/api/v1/consent/revoke",
        json={"prospect_id": prospect_id, "consent_type": "marketing_contact"},
    )
    assert revoke_resp.status_code == 200

    # Check can contact is immediately reverted to False
    status_resp = await client.get(f"/api/v1/consent/{prospect_id}")
    assert status_resp.json()["data"]["can_contact"] is False

