"""Synthetic extraction snapshot from manual POST."""
import uuid

import pytest


def test_manual_extracted_details_latest(auth_client):
    """POST manual snapshot is readable via GET extracted-details/latest."""
    client, _ = auth_client
    create = client.post(
        "/job-openings",
        json={
            "company_name": f"ManualCorp {uuid.uuid4().hex[:8]}",
            "role_name": "Analyst",
            "notes": "",
        },
    )
    assert create.status_code == 201, create.text
    oid = create.json()["id"]

    body = {
        "job_title": "Data Analyst",
        "company_name": "Widgets Inc",
        "location": "Remote",
        "description_summary": "Analyze metrics and build dashboards.",
        "required_skills": ["Python", "SQL"],
    }
    try:
        resp = client.post(f"/job-openings/{oid}/extracted-details/manual", json=body)
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["job_title"] == "Data Analyst"
        assert data["company_name"] == "Widgets Inc"
        assert data["extractor_model"] == "manual"
        assert "Python" in (data["required_skills"] or [])

        latest = client.get(f"/job-openings/{oid}/extracted-details/latest")
        assert latest.status_code == 200, latest.text
        assert latest.json()["extractor_model"] == "manual"
    finally:
        client.delete(f"/job-openings/{oid}?confirm=true")
