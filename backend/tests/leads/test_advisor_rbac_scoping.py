"""Tests for Advisor Queue and Strict RBAC Scoping."""
import pytest


@pytest.mark.asyncio
async def test_advisor_can_only_view_assigned_leads(client, admin_auth, advisor_auth, second_advisor_auth):
    # Create Lead 1 and assign to Advisor 1
    resp1 = await client.post(
        "/api/v1/prospects",
        json={"name": "Lead For Advisor 1", "email": "lead1@example.com", "initial_session_id": "sess-l1"},
    )
    lead1_id = resp1.json()["data"]["id"]
    await client.post(
        f"/api/v1/prospects/{lead1_id}/assign",
        headers=admin_auth,
        json={"advisor_id": advisor_auth["advisor"].id},
    )

    # Create Lead 2 and assign to Advisor 2
    resp2 = await client.post(
        "/api/v1/prospects",
        json={"name": "Lead For Advisor 2", "email": "lead2@example.com", "initial_session_id": "sess-l2"},
    )
    lead2_id = resp2.json()["data"]["id"]
    await client.post(
        f"/api/v1/prospects/{lead2_id}/assign",
        headers=admin_auth,
        json={"advisor_id": second_advisor_auth["advisor"].id},
    )

    # Advisor 1 views their queue
    queue1_resp = await client.get("/api/v1/advisor/leads", headers=advisor_auth)
    assert queue1_resp.status_code == 200
    queue1_items = queue1_resp.json()["items"]
    queue1_ids = [item["id"] for item in queue1_items]
    assert lead1_id in queue1_ids
    assert lead2_id not in queue1_ids

    # Advisor 1 attempts to access Lead 2 detail directly: MUST BE 403 FORBIDDEN
    denied_resp = await client.get(f"/api/v1/prospects/{lead2_id}", headers=advisor_auth)
    assert denied_resp.status_code == 403


@pytest.mark.asyncio
async def test_advisor_outreach_consent_blocked(client, admin_auth, advisor_auth):
    # Create Lead and assign to Advisor 1
    resp = await client.post(
        "/api/v1/prospects",
        json={"name": "Unconsented Lead", "phone": "+919000011111", "initial_session_id": "sess-unconsented"},
    )
    lead_id = resp.json()["data"]["id"]
    await client.post(
        f"/api/v1/prospects/{lead_id}/assign",
        headers=admin_auth,
        json={"advisor_id": advisor_auth["advisor"].id},
    )

    # Attempt to log outreach without consent: MUST BE 403 FORBIDDEN
    outreach_resp = await client.post(
        f"/api/v1/advisor/leads/{lead_id}/notes",
        headers=advisor_auth,
        json={
            "outcome": "connected_interested",
            "notes": "Spoke regarding Term Life plans",
            "schedule_follow_up": False,
            "follow_up_channel": "phone",
        },
    )
    assert outreach_resp.status_code == 403
    assert "consent" in outreach_resp.json()["message"].lower() or "consent" in str(outreach_resp.json()).lower()

