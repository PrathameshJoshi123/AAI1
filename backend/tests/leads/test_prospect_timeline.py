"""Tests for Unified Chronological Activity Timeline."""
import pytest


@pytest.mark.asyncio
async def test_prospect_timeline_aggregation(client, admin_auth, advisor_auth):
    # 1. Ingest lead
    resp = await client.post(
        "/api/v1/prospects",
        json={"name": "Vikram Seth", "email": "vikram@example.com", "initial_session_id": "sess-vikram"},
    )
    prospect_id = resp.json()["data"]["id"]

    # 2. Grant consent
    await client.post(
        "/api/v1/consent",
        json={"prospect_id": prospect_id, "consent_type": "marketing_contact", "consent_version": "2026.1"},
    )

    # 3. Ingest calculator signal
    await client.post(
        "/api/v1/signals",
        json={
            "session_id": "sess-vikram",
            "prospect_id": prospect_id,
            "signal_type": "coverage_calculator_used",
            "payload_json": {"sum_assured": 10000000},
        },
    )

    # 4. Assign advisor
    await client.post(
        f"/api/v1/prospects/{prospect_id}/assign",
        headers=admin_auth,
        json={"advisor_id": advisor_auth["advisor"].id, "notes": "Auto-routed to licensed agent"},
    )

    # 5. Log outreach
    await client.post(
        f"/api/v1/advisor/leads/{prospect_id}/notes",
        headers=advisor_auth,
        json={
            "outcome": "connected_interested",
            "notes": "Discussed term insurance with rider",
            "schedule_follow_up": True,
            "follow_up_channel": "phone",
        },
    )

    # 6. Fetch timeline
    tl_resp = await client.get(f"/api/v1/prospects/{prospect_id}/timeline", headers=admin_auth)
    assert tl_resp.status_code == 200
    events = tl_resp.json()["data"]

    # Ensure all expected events are captured
    event_types = [e["event_type"] for e in events]
    assert "PROSPECT_CREATED" in event_types
    assert "CONSENT_GRANTED" in event_types
    assert "BEHAVIORAL_SIGNAL" in event_types
    assert "SCORE_RECALCULATED" in event_types
    assert "LEAD_ADVISOR_ASSIGNMENT" in event_types
    assert "ADVISOR_OUTREACH" in event_types

    # Verify descending chronological order
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps, reverse=True)

