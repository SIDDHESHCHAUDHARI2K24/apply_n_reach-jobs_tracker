"""Pytest fixtures for job_profile latex_resume section tests."""
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
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_client(app):
    """Yields (client, user_data, jp_id) — job profile created and personal details set."""
    async def _setup():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"jp-latex-test-{uuid.uuid4().hex}@example.com"
            user = await create_user(conn, email=email, password_hash=hash_password("pass"))
            return dict(user)
        finally:
            await conn.close()

    user_data = asyncio.run(_setup())

    async def override():
        return user_data

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as c:
        # Create user profile (needed for personal details)
        resp = c.post("/profile")
        assert resp.status_code in (201, 409)

        # Create job profile
        jp_resp = c.post("/job-profiles", json={
            "profile_name": f"Latex Test {uuid.uuid4().hex[:6]}",
            "target_role": "Software Engineer",
        })
        assert jp_resp.status_code == 201
        jp_id = jp_resp.json()["id"]

        # Set personal details (needed for header generation)
        c.patch(f"/job-profiles/{jp_id}/personal", json={
            "full_name": "Test User",
            "email": "test@example.com",
            "linkedin_url": "https://linkedin.com/in/testuser",
        })

        yield c, user_data, jp_id

    app.dependency_overrides.clear()
