"""Router HTTP status code tests for LinkedIn import."""

import asyncio
import uuid

import asyncpg
import pytest

from app.app import create_app
from app.features.auth.models import ensure_auth_schema, create_user
from app.features.auth.utils import get_current_user, hash_password
from app.features.core.config import settings
from app.features.user_profile.linkedin_import.errors import (
    LinkedInImportAppError,
    ImportStage,
    ErrorCode,
)
from app.features.user_profile.linkedin_import.router import router as linkedin_router
from app.features.user_profile.linkedin_import.schemas import MappedLinkedInProfile, MappedPersonal


async def _create_user_without_profile():
    conn = await asyncpg.connect(settings.database_url)
    try:
        await ensure_auth_schema(conn)
        email = f"test-linkedin-{uuid.uuid4().hex}@example.com"
        user = await create_user(
            conn, email=email, password_hash=hash_password("testpass")
        )
        return dict(user)
    finally:
        await conn.close()


def _make_client_with_user(user_data):
    app = create_app()
    app.include_router(linkedin_router)

    async def override_get_current_user():
        return user_data

    app.dependency_overrides[get_current_user] = override_get_current_user

    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.mark.parametrize(
    "error, expected_status, expected_code",
    [
        (
            LinkedInImportAppError(
                "token missing",
                stage=ImportStage.config,
                code=ErrorCode.MISSING_API_TOKEN,
                http_status=503,
            ),
            503,
            "MISSING_API_TOKEN",
        ),
        (
            LinkedInImportAppError(
                "invalid url",
                stage=ImportStage.validation,
                code=ErrorCode.INVALID_LINKEDIN_URL,
                http_status=422,
            ),
            422,
            "INVALID_LINKEDIN_URL",
        ),
        (
            LinkedInImportAppError(
                "upstream failed",
                stage=ImportStage.scrape,
                code=ErrorCode.UPSTREAM_ERROR,
                http_status=502,
            ),
            502,
            "UPSTREAM_ERROR",
        ),
    ],
)
class TestRouterScrapeErrors:
    """Test router maps scrape-stage LinkedInImportAppError to correct HTTP status."""

    def test_scrape_error_status_codes(
        self, auth_client, error, expected_status, expected_code, monkeypatch
    ):
        client, _, _ = auth_client
        from app.features.user_profile.linkedin_import import router as router_mod

        async def mock_scrape(*args, **kwargs):
            raise error

        monkeypatch.setattr(router_mod, "scrape_linkedin_profile", mock_scrape)

        response = client.post(
            "/profile/import/linkedin",
            json={"linkedin_url": "https://www.linkedin.com/in/test"},
        )
        assert response.status_code == expected_status
        detail = response.json()["detail"]
        assert detail["error_code"] == expected_code
        assert detail["stage"] == error.stage.value
        assert detail["message"] == str(error)


@pytest.mark.usefixtures("auth_client")
class TestRouterMappingError:
    """Test router maps mapping-stage LinkedInImportAppError to 424."""

    def test_mapping_failure_returns_424(self, auth_client, monkeypatch):
        client, _, _ = auth_client
        from app.features.user_profile.linkedin_import import router as router_mod

        async def mock_scrape(*args, **kwargs):
            return {"dummy": "data"}

        async def mock_map(*args, **kwargs):
            raise LinkedInImportAppError(
                "LLM failed",
                stage=ImportStage.map,
                code=ErrorCode.LLM_FAILURE,
                http_status=424,
            )

        monkeypatch.setattr(router_mod, "scrape_linkedin_profile", mock_scrape)
        monkeypatch.setattr(router_mod, "map_linkedin_to_profile", mock_map)

        response = client.post(
            "/profile/import/linkedin",
            json={"linkedin_url": "https://www.linkedin.com/in/test"},
        )
        assert response.status_code == 424
        detail = response.json()["detail"]
        assert detail["error_code"] == "LLM_FAILURE"
        assert detail["stage"] == "map"


class TestRouterHappyPath:
    """Test successful LinkedIn import."""

    def test_happy_path_returns_200(self, auth_client, monkeypatch):
        client, _, _ = auth_client
        from app.features.user_profile.linkedin_import import router as router_mod

        async def mock_scrape(*args, **kwargs):
            return {"name": "John Doe", "headline": "Engineer"}

        async def mock_map(*args, **kwargs):
            return MappedLinkedInProfile(
                personal=MappedPersonal(full_name="John Doe"),
            )

        async def mock_replace(*args, **kwargs):
            return {"personal": 1}

        monkeypatch.setattr(router_mod, "scrape_linkedin_profile", mock_scrape)
        monkeypatch.setattr(router_mod, "map_linkedin_to_profile", mock_map)
        monkeypatch.setattr(router_mod, "replace_profile_from_linkedin", mock_replace)

        response = client.post(
            "/profile/import/linkedin",
            json={"linkedin_url": "https://www.linkedin.com/in/johndoe"},
        )
        assert response.status_code == 200
        body = response.json()
        assert "imported successfully" in body["message"]
        assert body["sections_imported"]["personal"] == 1


class TestRouterMissingProfile:
    """Test 404 when user has no user_profiles row."""

    def test_missing_profile_returns_404(self):
        user_data = asyncio.run(_create_user_without_profile())
        client = _make_client_with_user(user_data)

        response = client.post(
            "/profile/import/linkedin",
            json={"linkedin_url": "https://www.linkedin.com/in/test"},
        )
        assert response.status_code == 404
        assert "profile not found" in response.json()["detail"].lower()
