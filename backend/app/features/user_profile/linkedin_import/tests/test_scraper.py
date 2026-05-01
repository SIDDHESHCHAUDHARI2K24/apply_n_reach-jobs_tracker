"""Unit tests for LinkedIn scraper — validate_linkedin_url and scrape_linkedin_profile."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from apify_client.errors import ApifyApiError

from app.features.user_profile.linkedin_import.errors import (
    ErrorCode,
    ImportStage,
    LinkedInImportAppError,
)
from app.features.user_profile.linkedin_import.scraper import (
    validate_linkedin_url,
    scrape_linkedin_profile,
)


class TestValidateLinkedInUrl:
    """Test validate_linkedin_url normalization and error raising."""

    def test_valid_url_returns_normalized(self):
        result = validate_linkedin_url("https://www.linkedin.com/in/foo")
        assert result == "https://www.linkedin.com/in/foo"

    def test_trailing_slash_stripped(self):
        result = validate_linkedin_url("https://www.linkedin.com/in/foo/")
        assert result == "https://www.linkedin.com/in/foo"

    def test_http_upgraded_to_https(self):
        result = validate_linkedin_url("http://www.linkedin.com/in/foo")
        assert result == "https://www.linkedin.com/in/foo"

    def test_bare_domain_prepended_with_https(self):
        result = validate_linkedin_url("www.linkedin.com/in/foo")
        assert result == "https://www.linkedin.com/in/foo"

    def test_empty_string_raises(self):
        with pytest.raises(LinkedInImportAppError) as exc:
            validate_linkedin_url("")
        assert exc.value.code == ErrorCode.INVALID_LINKEDIN_URL
        assert exc.value.stage == ImportStage.validation
        assert exc.value.http_status == 422

    def test_whitespace_only_raises(self):
        with pytest.raises(LinkedInImportAppError) as exc:
            validate_linkedin_url("   ")
        assert exc.value.code == ErrorCode.INVALID_LINKEDIN_URL
        assert exc.value.http_status == 422

    def test_non_linkedin_url_raises(self):
        with pytest.raises(LinkedInImportAppError) as exc:
            validate_linkedin_url("https://evil.com/in/foo")
        assert exc.value.code == ErrorCode.INVALID_LINKEDIN_URL
        assert exc.value.http_status == 422

    def test_linkedin_company_url_accepted(self):
        result = validate_linkedin_url("https://www.linkedin.com/company/foo")
        assert result == "https://www.linkedin.com/company/foo"


@pytest.fixture
def mock_apify_client():
    with patch(
        "app.features.user_profile.linkedin_import.scraper.ApifyClientAsync"
    ) as mock:
        yield mock


@pytest.fixture
def mock_settings_with_token():
    with patch(
        "app.features.user_profile.linkedin_import.scraper.get_settings"
    ) as mock_get:
        mock_get.return_value.apify_api_token = "test-token-123"
        yield mock_get


@pytest.fixture
def mock_settings_no_token():
    with patch(
        "app.features.user_profile.linkedin_import.scraper.get_settings"
    ) as mock_get:
        mock_get.return_value.apify_api_token = None
        yield mock_get


def _make_apify_error(status_code: int) -> ApifyApiError:
    """Create an ApifyApiError with the given status_code, bypassing the
    constructor (which requires a real impit.Response object)."""
    err = ApifyApiError.__new__(ApifyApiError)
    err.status_code = status_code
    return err


ACTOR_ID = "harvestapi~linkedin-profile-scraper"


class TestScrapeLinkedInProfile:
    """Test scrape_linkedin_profile with mocked ApifyClientAsync."""

    @pytest.mark.asyncio
    async def test_missing_token(self, mock_settings_no_token):
        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.MISSING_API_TOKEN
        assert exc.value.stage == ImportStage.config
        assert exc.value.http_status == 503

    @pytest.mark.asyncio
    async def test_happy_path(self, mock_settings_with_token, mock_apify_client):
        mock_instance = MagicMock()
        mock_apify_client.return_value = mock_instance

        # Mock actor().call() to return run result
        mock_actor = MagicMock()
        mock_instance.actor.return_value = mock_actor
        mock_actor.call = AsyncMock(return_value={
            "id": "run-123",
            "defaultDatasetId": "dataset-456",
        })

        # Mock dataset().list_items() to return profile data
        mock_dataset = MagicMock()
        mock_instance.dataset.return_value = mock_dataset
        mock_dataset.list_items = AsyncMock(return_value=MagicMock(
            items=[{"firstName": "John", "lastName": "Doe", "headline": "Engineer"}]
        ))

        result = await scrape_linkedin_profile("https://www.linkedin.com/in/john")

        assert result["firstName"] == "John"
        assert result["lastName"] == "Doe"
        mock_instance.actor.assert_called_once_with(ACTOR_ID)
        mock_instance.dataset.assert_called_once_with("dataset-456")

    @pytest.mark.asyncio
    async def test_empty_items(self, mock_settings_with_token, mock_apify_client):
        mock_instance = MagicMock()
        mock_apify_client.return_value = mock_instance

        mock_actor = MagicMock()
        mock_instance.actor.return_value = mock_actor
        mock_actor.call = AsyncMock(return_value={
            "id": "run-123",
            "defaultDatasetId": "dataset-456",
        })

        mock_dataset = MagicMock()
        mock_instance.dataset.return_value = mock_dataset
        mock_dataset.list_items = AsyncMock(return_value=MagicMock(items=[]))

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.EMPTY_SCRAPE_RESULT
        assert exc.value.http_status == 422

    @pytest.mark.asyncio
    async def test_actor_error_result(self, mock_settings_with_token, mock_apify_client):
        mock_instance = MagicMock()
        mock_apify_client.return_value = mock_instance

        mock_actor = MagicMock()
        mock_instance.actor.return_value = mock_actor
        mock_actor.call = AsyncMock(return_value={
            "id": "run-123",
            "defaultDatasetId": "dataset-456",
        })

        mock_dataset = MagicMock()
        mock_instance.dataset.return_value = mock_dataset
        mock_dataset.list_items = AsyncMock(return_value=MagicMock(
            items=[{"status": "error", "error": "blocked"}]
        ))

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.EMPTY_SCRAPE_RESULT
        assert exc.value.http_status == 422

    @pytest.mark.asyncio
    async def test_401(self, mock_settings_with_token, mock_apify_client):
        mock_instance = MagicMock()
        mock_apify_client.return_value = mock_instance

        mock_actor = MagicMock()
        mock_instance.actor.return_value = mock_actor
        mock_actor.call = AsyncMock(side_effect=_make_apify_error(401))

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.APIFY_BAD_CREDENTIALS
        assert exc.value.http_status == 502

    @pytest.mark.asyncio
    async def test_429(self, mock_settings_with_token, mock_apify_client):
        mock_instance = MagicMock()
        mock_apify_client.return_value = mock_instance

        mock_actor = MagicMock()
        mock_instance.actor.return_value = mock_actor
        mock_actor.call = AsyncMock(side_effect=_make_apify_error(429))

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.APIFY_QUOTA_EXCEEDED
        assert exc.value.http_status == 502

    @pytest.mark.asyncio
    async def test_invalid_url(self, mock_settings_no_token):
        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://evil.com/in/foo")
        assert exc.value.code == ErrorCode.INVALID_LINKEDIN_URL
        assert exc.value.stage == ImportStage.validation
        assert exc.value.http_status == 422
