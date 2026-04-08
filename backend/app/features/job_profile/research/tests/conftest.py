"""Pytest fixtures for job_profile research feature tests."""
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
    from app.features.job_profile.core.router import router as core_router
    application.include_router(core_router)
    from app.features.job_profile.research.router import router as research_router
    application.include_router(research_router)
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
            email = f"jp-research-test-{uuid.uuid4().hex}@example.com"
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
