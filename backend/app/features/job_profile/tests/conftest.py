"""Shared test fixtures for all job_profile tests."""
import uuid
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.utils import get_current_user
from app.features.core.config import settings
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import hash_password


@pytest.fixture
def app():
    application = create_app()
    # Register job_profile router (will be done globally in Unit 9)
    from app.features.job_profile.core.router import router as job_profile_router
    application.include_router(job_profile_router)
    return application


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_client(app):
    """Yields (client, user_data, profile_id) where user_profile is created."""
    async def _setup():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"jp-test-{uuid.uuid4().hex}@example.com"
            user = await create_user(conn, email=email, password_hash=hash_password("pass"))
            return dict(user)
        finally:
            await conn.close()

    user_data = asyncio.run(_setup())

    async def override():
        return user_data

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as c:
        # Create user_profile for this user (needed for import tests)
        resp = c.post("/profile")
        assert resp.status_code in (201, 409), f"Profile creation failed: {resp.status_code}"

        if resp.status_code == 201:
            profile_id = resp.json()["id"]
        else:
            profile_id = None

        yield c, user_data, profile_id

    app.dependency_overrides.clear()


def _create_job_profile(client, **overrides):
    """Helper to create a job profile with defaults."""
    payload = {
        "profile_name": f"Test Resume {uuid.uuid4().hex[:8]}",
        "target_role": "Software Engineer",
        "target_company": "TestCorp",
        **overrides
    }
    resp = client.post("/job-profiles", json=payload)
    assert resp.status_code == 201, f"Failed to create job profile: {resp.status_code} {resp.text}"
    return resp.json()


def _create_user_profile_data(client):
    """Populate master profile with sample data for import tests.
    Returns dict of {section: [ids]}."""
    edu1 = client.post("/profile/education", json={
        "university_name": "MIT", "major": "CS", "degree_type": "BS",
        "start_month_year": "09/2018", "end_month_year": "06/2022"
    }).json()
    edu2 = client.post("/profile/education", json={
        "university_name": "Stanford", "major": "AI", "degree_type": "MS",
        "start_month_year": "09/2022"
    }).json()
    exp1 = client.post("/profile/experience", json={
        "role_title": "Engineer", "company_name": "Google",
        "start_month_year": "07/2022", "context": "Backend work"
    }).json()
    exp2 = client.post("/profile/experience", json={
        "role_title": "Intern", "company_name": "Meta",
        "start_month_year": "06/2021", "end_month_year": "08/2021",
        "context": "Frontend work"
    }).json()
    proj1 = client.post("/profile/projects", json={
        "project_name": "My App", "description": "A cool app",
        "start_month_year": "01/2023"
    }).json()
    res1 = client.post("/profile/research", json={
        "paper_name": "ML Paper", "publication_link": "https://arxiv.org/abs/1234",
        "description": "Research on ML"
    }).json()
    cert1 = client.post("/profile/certifications", json={
        "certification_name": "AWS SAA", "verification_link": "https://aws.amazon.com/cert"
    }).json()
    client.patch("/profile/skills", json={"skills": [
        {"kind": "technical", "name": "Python", "sort_order": 0},
        {"kind": "technical", "name": "FastAPI", "sort_order": 1},
        {"kind": "competency", "name": "Leadership", "sort_order": 0},
    ]})
    # Get skill IDs
    skills_resp = client.get("/profile/skills")
    skill_ids = [s["id"] for s in skills_resp.json()]

    return {
        "education": [edu1["id"], edu2["id"]],
        "experience": [exp1["id"], exp2["id"]],
        "projects": [proj1["id"]],
        "research": [res1["id"]],
        "certifications": [cert1["id"]],
        "skills": skill_ids,
    }
