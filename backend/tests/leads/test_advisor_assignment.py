"""Tests for Workload-Aware and Manual Advisor Assignment."""
import pytest


@pytest.mark.asyncio
async def test_manual_advisor_assignment_with_audit(client, admin_auth, advisor_auth):
    # Ingest lead
    resp = await client.post(
        "/api/v1/prospects",
        json={"name": "Sanjay Verma", "email": "sanjay@example.com", "initial_session_id": "sess-sanjay"},
    )
    prospect_id = resp.json()["data"]["id"]

    advisor_id = advisor_auth["advisor"].id

    # Manually assign advisor
    assign_resp = await client.post(
        f"/api/v1/prospects/{prospect_id}/assign",
        headers=admin_auth,
        json={"advisor_id": advisor_id, "notes": "High net-worth prospect requested senior advisor"},
    )
    assert assign_resp.status_code == 200
    data = assign_resp.json()["data"]
    assert data["assigned_advisor_id"] == advisor_id

    # Verify timeline reflects assignment
    tl_resp = await client.get(f"/api/v1/prospects/{prospect_id}/timeline", headers=admin_auth)
    assert tl_resp.status_code == 200
    events = tl_resp.json()["data"]
    event_types = [e["event_type"] for e in events]
    assert "LEAD_ADVISOR_ASSIGNMENT" in event_types


@pytest.mark.asyncio
async def test_advisor_workload_metrics(client, admin_auth, advisor_auth):
    resp = await client.get("/api/v1/prospects/advisors", headers=admin_auth)
    assert resp.status_code == 200
    advisors = resp.json()["data"]
    assert len(advisors) >= 1
    target = next((a for a in advisors if a["advisor_id"] == advisor_auth["advisor"].id), None)
    assert target is not None
    assert target["license_number"] == "ADV-9999"
    assert target["max_active_cases"] == 10
    assert target["is_available"] is True

