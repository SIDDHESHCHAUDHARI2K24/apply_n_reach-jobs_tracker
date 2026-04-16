"""Tests for opening resume section CRUD endpoints."""
import asyncio
import uuid

import asyncpg
import pytest

from app.features.core.config import settings
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password


# ─────────────────────────── Personal tests ───────────────────────────


def test_get_personal_200(auth_client, sample_resume, sample_opening):
    """GET personal section returns 200."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/personal")
    assert resp.status_code == 200
    data = resp.json()
    assert data["resume_id"] == sample_resume["id"]
    assert data["full_name"] == "Test User"


def test_put_personal_upsert(auth_client, sample_resume, sample_opening):
    """PUT personal section updates existing row."""
    client, _ = auth_client
    resp = client.put(
        f"/job-openings/{sample_opening['id']}/resume/personal",
        json={
            "full_name": "Updated Name",
            "email": "updated@example.com",
            "phone": "555-1234",
            "location": "San Francisco, CA",
            "summary": "Updated summary text",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "Updated Name"
    assert data["phone"] == "555-1234"
    assert data["location"] == "San Francisco, CA"


def test_put_personal_creates_if_not_exists(auth_client, sample_resume, sample_opening):
    """PUT personal after deleting personal row creates a new row."""
    client, _ = auth_client

    # Delete the personal row directly
    async def _delete_personal():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await conn.execute(
                "DELETE FROM job_opening_personal WHERE resume_id=$1",
                sample_resume["id"],
            )
        finally:
            await conn.close()

    asyncio.run(_delete_personal())

    resp = client.put(
        f"/job-openings/{sample_opening['id']}/resume/personal",
        json={"full_name": "New Person", "email": "new@example.com"},
    )
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "New Person"


# ─────────────────────────── Education CRUD tests ───────────────────────────


def test_list_education_200(auth_client, sample_resume, sample_opening):
    """GET education list returns 200 with copied snapshot data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/education")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["institution"] == "MIT"


def test_create_education_201(auth_client, sample_resume, sample_opening):
    """POST education returns 201 with new entry."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/education",
        json={
            "institution": "Stanford University",
            "degree": "Master",
            "field_of_study": "AI",
            "start_date": "09/2022",
            "end_date": "06/2024",
            "display_order": 1,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["institution"] == "Stanford University"
    assert data["degree"] == "Master"
    assert data["resume_id"] == sample_resume["id"]


def test_get_education_entry_200(auth_client, sample_resume, sample_opening):
    """GET education/{id} returns 200 for existing entry."""
    client, _ = auth_client
    # Create an entry first
    create_resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/education",
        json={"institution": "Test Uni", "degree": "PhD", "display_order": 2},
    )
    assert create_resp.status_code == 201
    entry_id = create_resp.json()["id"]

    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/education/{entry_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == entry_id


def test_patch_education_200(auth_client, sample_resume, sample_opening):
    """PATCH education/{id} updates specified fields."""
    client, _ = auth_client
    create_resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/education",
        json={"institution": "Old Uni", "display_order": 3},
    )
    assert create_resp.status_code == 201
    entry_id = create_resp.json()["id"]

    resp = client.patch(
        f"/job-openings/{sample_opening['id']}/resume/education/{entry_id}",
        json={"institution": "New Uni"},
    )
    assert resp.status_code == 200
    assert resp.json()["institution"] == "New Uni"


def test_delete_education_204(auth_client, sample_resume, sample_opening):
    """DELETE education/{id} returns 204 and removes entry."""
    client, _ = auth_client
    create_resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/education",
        json={"institution": "Temp Uni", "display_order": 4},
    )
    assert create_resp.status_code == 201
    entry_id = create_resp.json()["id"]

    resp = client.delete(
        f"/job-openings/{sample_opening['id']}/resume/education/{entry_id}"
    )
    assert resp.status_code == 204

    # Verify it's gone
    get_resp = client.get(
        f"/job-openings/{sample_opening['id']}/resume/education/{entry_id}"
    )
    assert get_resp.status_code == 404


def test_education_not_found_404(auth_client, sample_resume, sample_opening):
    """GET education/{nonexistent_id} returns 404."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/education/999999")
    assert resp.status_code == 404


# ─────────────────────────── Skills CRUD tests ───────────────────────────


def test_list_skills_200(auth_client, sample_resume, sample_opening):
    """GET skills list returns 200 with snapshot data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/skills")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    names = [s["name"] for s in data]
    assert "Python" in names


def test_create_skill_201(auth_client, sample_resume, sample_opening):
    """POST skill returns 201 with new entry."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/skills",
        json={"category": "technical", "name": "FastAPI", "display_order": 0},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "FastAPI"
    assert data["category"] == "technical"


def test_patch_skill_200(auth_client, sample_resume, sample_opening):
    """PATCH skill/{id} updates specified fields."""
    client, _ = auth_client
    create_resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/skills",
        json={"category": "technical", "name": "Docker", "display_order": 0},
    )
    assert create_resp.status_code == 201
    skill_id = create_resp.json()["id"]

    resp = client.patch(
        f"/job-openings/{sample_opening['id']}/resume/skills/{skill_id}",
        json={"proficiency_level": "Advanced"},
    )
    assert resp.status_code == 200
    assert resp.json()["proficiency_level"] == "Advanced"


def test_delete_skill_204(auth_client, sample_resume, sample_opening):
    """DELETE skill/{id} returns 204."""
    client, _ = auth_client
    create_resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/skills",
        json={"category": "competency", "name": "Temp Skill", "display_order": 99},
    )
    assert create_resp.status_code == 201
    skill_id = create_resp.json()["id"]

    resp = client.delete(
        f"/job-openings/{sample_opening['id']}/resume/skills/{skill_id}"
    )
    assert resp.status_code == 204


# ─────────────────────────── Projects JSONB tests ───────────────────────────


def test_create_project_with_technologies(auth_client, sample_resume, sample_opening):
    """POST project with technologies JSONB field."""
    client, _ = auth_client
    resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/projects",
        json={
            "name": "My App",
            "description": "A cool app",
            "technologies": ["Python", "FastAPI", "PostgreSQL"],
            "display_order": 0,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My App"
    assert data["technologies"] == ["Python", "FastAPI", "PostgreSQL"]


def test_patch_project_technologies(auth_client, sample_resume, sample_opening):
    """PATCH project updates technologies JSONB field."""
    client, _ = auth_client
    create_resp = client.post(
        f"/job-openings/{sample_opening['id']}/resume/projects",
        json={"name": "Tech App", "technologies": ["Python"], "display_order": 0},
    )
    assert create_resp.status_code == 201
    proj_id = create_resp.json()["id"]

    resp = client.patch(
        f"/job-openings/{sample_opening['id']}/resume/projects/{proj_id}",
        json={"technologies": ["Python", "Docker", "Redis"]},
    )
    assert resp.status_code == 200
    assert resp.json()["technologies"] == ["Python", "Docker", "Redis"]


# ─────────────────────────── Cross-user isolation ───────────────────────────


def test_cross_user_cannot_access_education(auth_client, sample_resume, sample_opening, app):
    """User B cannot access User A's resume education entries — returns 404."""

    async def _create_user_b():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-b-edu-{uuid.uuid4().hex}@example.com"
            user = await create_user(
                conn, email=email, password_hash=hash_password("testpass")
            )
            return dict(user)
        finally:
            await conn.close()

    user_b = asyncio.run(_create_user_b())

    from fastapi.testclient import TestClient

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as client_b:
        resp = client_b.get(f"/job-openings/{sample_opening['id']}/resume/education")
    app.dependency_overrides.clear()

    assert resp.status_code == 404


def test_cross_user_cannot_access_personal(auth_client, sample_resume, sample_opening, app):
    """User B cannot access User A's resume personal section — returns 404."""

    async def _create_user_b():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-b-personal-{uuid.uuid4().hex}@example.com"
            user = await create_user(
                conn, email=email, password_hash=hash_password("testpass")
            )
            return dict(user)
        finally:
            await conn.close()

    user_b = asyncio.run(_create_user_b())

    from fastapi.testclient import TestClient

    async def override_b():
        return user_b

    app.dependency_overrides[get_current_user] = override_b
    with TestClient(app) as client_b:
        resp = client_b.get(f"/job-openings/{sample_opening['id']}/resume/personal")
    app.dependency_overrides.clear()

    assert resp.status_code == 404


# ─────────────────────────── Other sections smoke tests ───────────────────────────


def test_list_experience_200(auth_client, sample_resume, sample_opening):
    """GET experience list returns snapshot data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/experience")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["company"] == "Acme Corp"
    assert data[0]["title"] == "Software Engineer"


def test_list_research_200(auth_client, sample_resume, sample_opening):
    """GET research list returns snapshot data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/research")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["title"] == "My Research Paper"


def test_list_certifications_200(auth_client, sample_resume, sample_opening):
    """GET certifications list returns snapshot data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/certifications")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "AWS Certified Developer"


def test_list_projects_200(auth_client, sample_resume, sample_opening):
    """GET projects list returns snapshot data."""
    client, _ = auth_client
    resp = client.get(f"/job-openings/{sample_opening['id']}/resume/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == "Cool Project"
