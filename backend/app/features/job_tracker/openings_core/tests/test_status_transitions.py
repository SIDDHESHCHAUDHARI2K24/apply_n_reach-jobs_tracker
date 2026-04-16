"""Tests for job opening status transitions."""
import uuid


def _create_opening(client, initial_status="Interested"):
    tag = uuid.uuid4().hex[:8]
    resp = client.post(
        "/job-openings",
        json={
            "company_name": f"Co {tag}",
            "role_name": "Engineer",
            "initial_status": initial_status,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _transition(client, opening_id, to_status):
    return client.post(f"/job-openings/{opening_id}/status", json={"status": to_status})


def test_interested_to_applied(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Interested")
    resp = _transition(client, opening["id"], "Applied")
    assert resp.status_code == 200
    assert resp.json()["current_status"] == "Applied"


def test_applied_to_interviewing(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Applied")
    resp = _transition(client, opening["id"], "Interviewing")
    assert resp.status_code == 200
    assert resp.json()["current_status"] == "Interviewing"


def test_interviewing_to_offer(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Interviewing")
    resp = _transition(client, opening["id"], "Offer")
    assert resp.status_code == 200
    assert resp.json()["current_status"] == "Offer"


def test_interested_to_withdrawn(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Interested")
    resp = _transition(client, opening["id"], "Withdrawn")
    assert resp.status_code == 200
    assert resp.json()["current_status"] == "Withdrawn"


def test_invalid_transition_interested_to_offer_400(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Interested")
    resp = _transition(client, opening["id"], "Offer")
    assert resp.status_code == 400
    detail = resp.json()["detail"].lower()
    assert "invalid status transition" in detail


def test_terminal_withdrawn_to_applied_400(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Withdrawn")
    resp = _transition(client, opening["id"], "Applied")
    assert resp.status_code == 400
    detail = resp.json()["detail"].lower()
    assert "invalid status transition" in detail


def test_terminal_rejected_to_interviewing_400(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Rejected")
    resp = _transition(client, opening["id"], "Interviewing")
    assert resp.status_code == 400


def test_status_history_ordered_after_multiple_transitions(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Interested")
    oid = opening["id"]

    _transition(client, oid, "Applied")
    _transition(client, oid, "Interviewing")
    _transition(client, oid, "Offer")

    resp = client.get(f"/job-openings/{oid}/status-history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) == 4  # initial + 3 transitions

    # Verify order: from_status/to_status sequence
    assert history[0]["from_status"] is None
    assert history[0]["to_status"] == "Interested"

    assert history[1]["from_status"] == "Interested"
    assert history[1]["to_status"] == "Applied"

    assert history[2]["from_status"] == "Applied"
    assert history[2]["to_status"] == "Interviewing"

    assert history[3]["from_status"] == "Interviewing"
    assert history[3]["to_status"] == "Offer"


def test_status_history_initial_entry(auth_client):
    client, _ = auth_client
    opening = _create_opening(client, "Applied")
    oid = opening["id"]

    resp = client.get(f"/job-openings/{oid}/status-history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) == 1
    assert history[0]["from_status"] is None
    assert history[0]["to_status"] == "Applied"


def test_status_history_404_unknown_opening(auth_client):
    client, _ = auth_client
    resp = client.get("/job-openings/999999999/status-history")
    assert resp.status_code == 404
