"""Tests for the delete confirmation guard."""


def test_delete_without_confirm_param_400(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.delete(f"/job-openings/{opening_id}")
    assert resp.status_code == 400
    assert "confirm" in resp.json()["detail"].lower()


def test_delete_with_confirm_false_400(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.delete(f"/job-openings/{opening_id}?confirm=false")
    assert resp.status_code == 400
    assert "confirm" in resp.json()["detail"].lower()


def test_delete_with_confirm_true_204(auth_client, sample_opening):
    client, _ = auth_client
    opening_id = sample_opening["id"]
    resp = client.delete(f"/job-openings/{opening_id}?confirm=true")
    assert resp.status_code == 204


def test_delete_nonexistent_opening_404(auth_client):
    client, _ = auth_client
    resp = client.delete("/job-openings/999999999?confirm=true")
    assert resp.status_code == 404
