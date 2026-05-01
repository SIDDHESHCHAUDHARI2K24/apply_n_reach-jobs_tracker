"""LinkedIn profile scraper using Apify."""
import asyncio
import logging

import httpx

from app.features.core.config import get_settings
from app.features.user_profile.linkedin_import.errors import (
    ErrorCode,
    ImportStage,
    LinkedInImportAppError,
)

logger = logging.getLogger(__name__)

_RETRYABLE_STATUSES = frozenset({429, 500, 502, 503, 504})
_MAX_RETRIES = 3
_RETRY_BACKOFF_BASE = 2.0


def validate_linkedin_url(url: str) -> str:
    """Validate and normalize a LinkedIn profile URL.

    Returns the normalized URL. Raises LinkedInImportAppError on invalid input.
    """
    stripped = url.strip().rstrip("/")
    if not stripped:
        raise LinkedInImportAppError(
            "LinkedIn URL is required",
            stage=ImportStage.validation,
            code=ErrorCode.INVALID_LINKEDIN_URL,
            http_status=422,
        )
    if "linkedin.com" not in stripped:
        raise LinkedInImportAppError(
            "URL does not appear to be a LinkedIn profile URL",
            stage=ImportStage.validation,
            code=ErrorCode.INVALID_LINKEDIN_URL,
            http_status=422,
        )
    if not stripped.startswith("https://"):
        stripped = stripped.replace("http://", "https://", 1)
        if not stripped.startswith("https://"):
            stripped = f"https://{stripped}"
    return stripped


async def _post_with_retry(client: httpx.AsyncClient, endpoint: str, token: str, url: str) -> dict:
    """POST to Apify with bounded retries for transient failures."""
    last_exc: Exception | None = None
    for attempt in range(1 + _MAX_RETRIES):
        try:
            response = await client.post(
                endpoint,
                params={"token": token},
                json={
                    "startUrls": [url],
                    "proxyConfiguration": {"useApifyProxy": True},
                },
            )
            if response.status_code in _RETRYABLE_STATUSES and attempt < _MAX_RETRIES:
                body_preview = response.text[:512]
                logger.warning(
                    "Apify transient error (attempt %d/%d) status=%d body=%s",
                    attempt + 1, 1 + _MAX_RETRIES, response.status_code, body_preview,
                )
                await asyncio.sleep(_RETRY_BACKOFF_BASE ** attempt)
                continue
            response.raise_for_status()
            items = response.json()
            if not items:
                raise LinkedInImportAppError(
                    "No profile data returned from Apify",
                    stage=ImportStage.scrape,
                    code=ErrorCode.EMPTY_SCRAPE_RESULT,
                    http_status=422,
                )
            return items[0]
        except LinkedInImportAppError:
            raise
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status in (401, 403):
                raise LinkedInImportAppError(
                    f"Apify authentication failed: {status}",
                    stage=ImportStage.scrape,
                    code=ErrorCode.APIFY_BAD_CREDENTIALS,
                    http_status=502,
                ) from e
            if status == 429:
                raise LinkedInImportAppError(
                    "Apify quota exceeded",
                    stage=ImportStage.scrape,
                    code=ErrorCode.APIFY_QUOTA_EXCEEDED,
                    http_status=502,
                ) from e
            body_preview = e.response.text[:512] if hasattr(e.response, "text") else "<no body>"
            logger.exception(
                "Apify upstream error status=%d body=%s", status, body_preview,
            )
            raise LinkedInImportAppError(
                f"Upstream error from Apify: {status}",
                stage=ImportStage.scrape,
                code=ErrorCode.UPSTREAM_ERROR,
                http_status=502,
            ) from e
        except httpx.HTTPError as e:
            last_exc = e
            if attempt < _MAX_RETRIES:
                logger.warning(
                    "HTTP error scraping LinkedIn (attempt %d/%d): %s",
                    attempt + 1, 1 + _MAX_RETRIES, e,
                )
                await asyncio.sleep(_RETRY_BACKOFF_BASE ** attempt)
                continue
            break

    raise LinkedInImportAppError(
        f"HTTP error scraping LinkedIn after {1 + _MAX_RETRIES} attempts: {last_exc}",
        stage=ImportStage.scrape,
        code=ErrorCode.RETRIES_EXHAUSTED,
        http_status=502,
    ) from last_exc


async def scrape_linkedin_profile(linkedin_url: str) -> dict:
    """Scrape a LinkedIn profile using Apify's harvestapi actor.

    Returns raw profile data dict. Raises LinkedInImportAppError on failure.
    """
    url = validate_linkedin_url(linkedin_url)
    logger.info("Validated LinkedIn URL, proceeding to scrape: %s", url)

    settings = get_settings()
    token = settings.apify_api_token
    if not token:
        raise LinkedInImportAppError(
            "Apify API token not configured",
            stage=ImportStage.config,
            code=ErrorCode.MISSING_API_TOKEN,
            http_status=503,
        )

    actor_id = "harvestapi~linkedin-profile-scraper"
    endpoint = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"

    async with httpx.AsyncClient(timeout=120.0) as client:
        return await _post_with_retry(client, endpoint, token, url)
