"""Unit tests for LinkedIn scraper — validate_linkedin_url and scrape_linkedin_profile."""

from unittest.mock import AsyncMock, patch

import pytest

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


@pytest.fixture
def mock_post_with_retry():
    with patch(
        "app.features.user_profile.linkedin_import.scraper._post_with_retry"
    ) as mock:
        yield mock


class TestScrapeLinkedInProfile:
    """Test scrape_linkedin_profile with mocked dependencies."""

    @pytest.mark.asyncio
    async def test_missing_token_raises_config_error(self, mock_settings_no_token):
        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.MISSING_API_TOKEN
        assert exc.value.stage == ImportStage.config
        assert exc.value.http_status == 503

    @pytest.mark.asyncio
    async def test_happy_path_returns_first_item(
        self, mock_settings_with_token, mock_post_with_retry
    ):
        mock_post_with_retry.return_value = {"name": "John", "headline": "Engineer"}

        result = await scrape_linkedin_profile("https://www.linkedin.com/in/john")

        assert result == {"name": "John", "headline": "Engineer"}

    @pytest.mark.asyncio
    async def test_empty_items_raises_error(
        self, mock_settings_with_token, mock_post_with_retry
    ):
        mock_post_with_retry.side_effect = LinkedInImportAppError(
            "No profile data returned from Apify",
            stage=ImportStage.scrape,
            code=ErrorCode.EMPTY_SCRAPE_RESULT,
            http_status=422,
        )

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.EMPTY_SCRAPE_RESULT
        assert exc.value.http_status == 422

    @pytest.mark.asyncio
    async def test_401_raises_bad_credentials(
        self, mock_settings_with_token, mock_post_with_retry
    ):
        mock_post_with_retry.side_effect = LinkedInImportAppError(
            "Apify authentication failed: 401",
            stage=ImportStage.scrape,
            code=ErrorCode.APIFY_BAD_CREDENTIALS,
            http_status=502,
        )

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.APIFY_BAD_CREDENTIALS
        assert exc.value.http_status == 502

    @pytest.mark.asyncio
    async def test_429_raises_quota_exceeded(
        self, mock_settings_with_token, mock_post_with_retry
    ):
        mock_post_with_retry.side_effect = LinkedInImportAppError(
            "Apify quota exceeded",
            stage=ImportStage.scrape,
            code=ErrorCode.APIFY_QUOTA_EXCEEDED,
            http_status=502,
        )

        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://www.linkedin.com/in/test")
        assert exc.value.code == ErrorCode.APIFY_QUOTA_EXCEEDED
        assert exc.value.http_status == 502

    @pytest.mark.asyncio
    async def test_invalid_url_before_token_check(
        self, mock_settings_no_token
    ):
        with pytest.raises(LinkedInImportAppError) as exc:
            await scrape_linkedin_profile("https://evil.com/in/foo")
        assert exc.value.code == ErrorCode.INVALID_LINKEDIN_URL
        assert exc.value.stage == ImportStage.validation
        assert exc.value.http_status == 422
