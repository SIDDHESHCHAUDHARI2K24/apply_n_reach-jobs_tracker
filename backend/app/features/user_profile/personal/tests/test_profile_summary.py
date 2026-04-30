"""Integration tests for GET /profile/summary endpoint."""
import uuid


def test_profile_summary_empty(authenticated_client):
    """Summary returns all zeros when profile exists but no data."""
    client, _ = authenticated_client
    client.post("/profile")
    resp = client.get("/profile/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["personal_details_exists"] is False
    assert data["education_count"] == 0
    assert data["experience_count"] == 0
    assert data["projects_count"] == 0
    assert data["research_count"] == 0
    assert data["certifications_count"] == 0
    assert data["skills_count"] == 0


def test_profile_summary_with_data(authenticated_client):
    """Summary reflects data created in profile sections."""
    client, _ = authenticated_client
    client.post("/profile")
    # Create personal details
    client.patch("/profile/personal", json={
        "full_name": "Test User",
        "email": f"summary-{uuid.uuid4().hex}@example.com",
        "linkedin_url": "https://linkedin.com/in/test",
    })
    # Create education entry
    client.post("/profile/education", json={
        "university_name": "MIT",
        "major": "CS",
        "degree_type": "BS",
        "start_month_year": "09/2018",
    })
    resp = client.get("/profile/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["personal_details_exists"] is True
    assert data["education_count"] == 1


def test_profile_summary_unauthenticated(client):
    """Summary endpoint requires authentication."""
    resp = client.get("/profile/summary")
    assert resp.status_code == 401


def test_profile_summary_no_profile_404(authenticated_client):
    """Summary returns 404 when no profile has been created."""
    client, _ = authenticated_client
    # Do NOT create profile
    resp = client.get("/profile/summary")
    assert resp.status_code == 404
