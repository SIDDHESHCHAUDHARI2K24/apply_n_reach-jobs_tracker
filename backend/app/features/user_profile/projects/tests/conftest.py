"""Pytest fixtures for projects sub-feature tests."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.utils import get_current_user
from app.features.user_profile.projects.router import router as projects_router


def make_app():
    """Create a fresh app instance for tests."""
    return create_app()


@pytest.fixture
def app():
    """Yield a FastAPI app instance with the projects router included."""
    a = make_app()
    a.include_router(projects_router)
    return a


@pytest.fixture
def client(app):
    """Yield an unauthenticated TestClient."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_client(app):
    """Yield a TestClient whose requests pass get_current_user without a real session.

    The current_user record is a minimal dict matching the asyncpg.Record interface
    (accessed by key like current_user["id"]). Uses a real user inserted into the DB.
    """
    import asyncio
    import asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password

    # Insert a real test user synchronously using asyncio.run
    async def _create_test_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-profile-{uuid.uuid4().hex}@example.com"
            user = await create_user(conn, email=email, password_hash=hash_password("testpass"))
            return dict(user)
        finally:
            await conn.close()

    user_data = asyncio.run(_create_test_user())

    # Override get_current_user to return this user as a dict (works like asyncpg.Record)
    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c, user_data

    app.dependency_overrides.clear()
