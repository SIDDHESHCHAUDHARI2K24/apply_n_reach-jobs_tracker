"""Cross-user isolation tests for job_tracker feature.

These tests verify that user B cannot access, modify, or delete resources
owned by user A — exercised through the fully wired app (all routers
registered via create_app()).
"""


def test_user_b_cannot_get_opening_a(user_b_client, opening_a):
    resp = user_b_client.get(f"/job-openings/{opening_a['id']}")
    assert resp.status_code == 404


def test_user_b_cannot_patch_opening_a(user_b_client, opening_a):
    resp = user_b_client.patch(
        f"/job-openings/{opening_a['id']}", json={"company_name": "Hack"}
    )
    assert resp.status_code == 404


def test_user_b_cannot_delete_opening_a(user_b_client, opening_a):
    resp = user_b_client.delete(f"/job-openings/{opening_a['id']}?confirm=true")
    assert resp.status_code == 404


def test_user_b_cannot_transition_status_of_opening_a(user_b_client, opening_a):
    resp = user_b_client.post(
        f"/job-openings/{opening_a['id']}/status", json={"status": "Applied"}
    )
    assert resp.status_code == 404


def test_user_b_cannot_refresh_extraction_on_opening_a(user_b_client, opening_a):
    resp = user_b_client.post(
        f"/job-openings/{opening_a['id']}/extraction/refresh"
    )
    assert resp.status_code == 404


def test_user_b_cannot_get_resume_of_opening_a(user_b_client, opening_a, resume_a):
    resp = user_b_client.get(f"/job-openings/{opening_a['id']}/resume")
    assert resp.status_code == 404


def test_user_b_cannot_get_education_of_opening_a(user_b_client, opening_a, resume_a):
    resp = user_b_client.get(f"/job-openings/{opening_a['id']}/resume/education")
    assert resp.status_code == 404
