"""Pytest fixtures for research feature tests."""
import uuid
import pytest
from fastapi.testclient import TestClient

from app.app import create_app
from app.features.auth.utils import get_current_user
from app.features.user_profile.research.router import router as research_router


def make_app():
    """Create a fresh app instance for tests."""
    return create_app()


@pytest.fixture
def app():
    a = make_app()
    a.include_router(research_router)
    return a


@pytest.fixture
def client(app):
    """Yield an unauthenticated TestClient."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def authenticated_client(app):
    """Yield a TestClient whose requests pass get_current_user without a real session."""
    import asyncio
    import asyncpg
    from app.features.core.config import settings
    from app.features.auth.models import ensure_auth_schema, create_user
    from app.features.auth.utils import hash_password

    async def _create_test_user():
        conn = await asyncpg.connect(settings.database_url)
        try:
            await ensure_auth_schema(conn)
            email = f"test-research-{uuid.uuid4().hex}@example.com"
            user = await create_user(conn, email=email, password_hash=hash_password("testpass"))
            return dict(user)
        finally:
            await conn.close()

    user_data = asyncio.run(_create_test_user())

    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as c:
        yield c, user_data

    app.dependency_overrides.clear()
