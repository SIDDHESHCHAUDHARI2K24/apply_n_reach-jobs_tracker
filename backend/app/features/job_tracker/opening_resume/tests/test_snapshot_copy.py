"""Tests for opening resume snapshot creation and copy semantics."""
import asyncio

import asyncpg
import pytest

from app.features.core.config import settings
from app.features.job_tracker.opening_resume.service import create_opening_resume


@pytest.fixture
def conn_and_user(auth_client, sample_job_profile, sample_opening):
    """Return (conn, user_id, opening_id, profile_id) via a shared connection."""
    _, user_data = auth_client
    return user_data["id"], sample_opening["id"], sample_job_profile["id"]


def test_create_resume_201(auth_client, sample_opening, sample_job_profile):
    """POST /job-openings/{id}/resume returns 201 with snapshot row."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume"
        f"?source_job_profile_id={sample_job_profile['id']}"
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["opening_id"] == sample_opening["id"]
    assert data["source_job_profile_id"] == sample_job_profile["id"]
    assert data["snapshot_version"] == 1
    assert data["source_section_count"] == 7


def test_get_resume_200(auth_client, sample_resume, sample_opening):
    """GET /job-openings/{id}/resume returns 200 with resume data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == sample_resume["id"]


def test_snapshot_copies_all_7_sections(auth_client, sample_opening, sample_job_profile):
    """Creating a snapshot copies data from all 7 job_profile sections."""
    _, user_data = auth_client

    async def _check():
        conn = await asyncpg.connect(settings.database_url)
        try:
            resume = await create_opening_resume(
                conn, user_data["id"], sample_opening["id"], sample_job_profile["id"]
            )
            resume_id = resume["id"]

            edu = await conn.fetch(
                "SELECT * FROM job_opening_education WHERE resume_id=$1", resume_id
            )
            exp = await conn.fetch(
                "SELECT * FROM job_opening_experience WHERE resume_id=$1", resume_id
            )
            proj = await conn.fetch(
                "SELECT * FROM job_opening_projects WHERE resume_id=$1", resume_id
            )
            res = await conn.fetch(
                "SELECT * FROM job_opening_research WHERE resume_id=$1", resume_id
            )
            cert = await conn.fetch(
                "SELECT * FROM job_opening_certifications WHERE resume_id=$1", resume_id
            )
            skills = await conn.fetch(
                "SELECT * FROM job_opening_skills WHERE resume_id=$1", resume_id
            )
            personal = await conn.fetch(
                "SELECT * FROM job_opening_personal WHERE resume_id=$1", resume_id
            )
            return resume_id, edu, exp, proj, res, cert, skills, personal
        finally:
            await conn.close()

    resume_id, edu, exp, proj, res, cert, skills, personal = asyncio.run(_check())

    assert len(edu) >= 1, "Education should have been copied"
    assert len(exp) >= 1, "Experience should have been copied"
    assert len(proj) >= 1, "Projects should have been copied"
    assert len(res) >= 1, "Research should have been copied"
    assert len(cert) >= 1, "Certifications should have been copied"
    assert len(skills) >= 2, "Skills should have been copied"
    assert len(personal) >= 1, "Personal should have been copied"


def test_snapshot_education_data_correct(auth_client, sample_opening, sample_job_profile):
    """Verify education snapshot maps source columns correctly."""
    _, user_data = auth_client

    async def _check():
        conn = await asyncpg.connect(settings.database_url)
        try:
            resume = await create_opening_resume(
                conn, user_data["id"], sample_opening["id"], sample_job_profile["id"]
            )
            edu = await conn.fetchrow(
                "SELECT * FROM job_opening_education WHERE resume_id=$1", resume["id"]
            )
            return dict(edu) if edu else None
        finally:
            await conn.close()

    edu = asyncio.run(_check())
    assert edu is not None
    assert edu["institution"] == "MIT"
    assert edu["field_of_study"] == "Computer Science"
    assert edu["degree"] == "Bachelor"
    assert edu["start_date"] == "09/2018"
    assert edu["end_date"] == "06/2022"


def test_duplicate_resume_409(auth_client, sample_opening, sample_resume, sample_job_profile):
    """Creating a second resume for the same opening returns 409."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume"
        f"?source_job_profile_id={sample_job_profile['id']}"
    )
    assert resp.status_code == 409


def test_post_copy_independence(auth_client, sample_opening, sample_job_profile):
    """Editing the snapshot does not affect the source job_profile data."""
    _, user_data = auth_client

    async def _check():
        conn = await asyncpg.connect(settings.database_url)
        try:
            resume = await create_opening_resume(
                conn, user_data["id"], sample_opening["id"], sample_job_profile["id"]
            )
            # Edit snapshot education
            await conn.execute(
                "UPDATE job_opening_education SET institution='SNAPSHOT EDIT' WHERE resume_id=$1",
                resume["id"],
            )
            # Source should be unchanged
            source_edu = await conn.fetchrow(
                "SELECT * FROM job_profile_educations WHERE job_profile_id=$1",
                sample_job_profile["id"],
            )
            snapshot_edu = await conn.fetchrow(
                "SELECT * FROM job_opening_education WHERE resume_id=$1", resume["id"]
            )
            return source_edu["university_name"], snapshot_edu["institution"]
        finally:
            await conn.close()

    source_val, snapshot_val = asyncio.run(_check())
    assert source_val != "SNAPSHOT EDIT", "Source should not be modified"
    assert snapshot_val == "SNAPSHOT EDIT", "Snapshot should be independently editable"


def test_cross_user_isolation_resume(auth_client, sample_resume, sample_opening, app):
    """User B cannot access User A's opening resume — returns 404."""
    import uuid
    from fastapi.testclient import TestClient
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import get_current_user, hash_password

    async def _create_user_b():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-resume-iso-{uuid.uuid4().hex}@example.com"
            user = await create_user(
                conn, email=email, password_hash=hash_password("testpass")
            )
            return dict(user)
        finally:
            await conn.close()

    user_b = asyncio.run(_create_user_b())

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as client_b:
        resp = client_b.get(f"/job-openings/{sample_opening['id']}/resume")
    app.dependency_overrides.clear()

    assert resp.status_code == 404


def test_opening_not_found_returns_404(auth_client, sample_job_profile):
    """POST to non-existent opening_id returns 404."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/999999/resume"
        f"?source_job_profile_id={sample_job_profile['id']}"
    )
    assert resp.status_code == 404


def test_job_profile_not_found_returns_404(auth_client, sample_opening):
    """POST with non-existent source_job_profile_id returns 404."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume?source_job_profile_id=999999"
    )
    assert resp.status_code == 404
