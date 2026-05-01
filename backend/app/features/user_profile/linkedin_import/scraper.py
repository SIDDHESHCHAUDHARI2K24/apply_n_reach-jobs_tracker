"""LinkedIn profile scraper using Apify."""
import logging

from apify_client import ApifyClientAsync
from apify_client.errors import ApifyApiError

from app.features.core.config import get_settings
from app.features.user_profile.linkedin_import.errors import (
    ErrorCode,
    ImportStage,
    LinkedInImportAppError,
)

logger = logging.getLogger(__name__)

ACTOR_ID = "harvestapi~linkedin-profile-scraper"
SCRAPER_MODE = "Profile details no email ($4 per 1k)"


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

    client = ApifyClientAsync(token=token)

    try:
        run = await client.actor(ACTOR_ID).call(
            run_input={
                "profileScraperMode": SCRAPER_MODE,
                "queries": [url],
            },
            wait_secs=120,
        )
    except LinkedInImportAppError:
        raise
    except ApifyApiError as e:
        status = getattr(e, "status_code", 0)
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
        logger.exception("Apify API error: %s", e)
        raise LinkedInImportAppError(
            f"Upstream error from Apify: {e}",
            stage=ImportStage.scrape,
            code=ErrorCode.UPSTREAM_ERROR,
            http_status=502,
        ) from e
    except Exception as e:
        logger.exception("Unexpected error scraping LinkedIn")
        raise LinkedInImportAppError(
            f"Error scraping LinkedIn: {e}",
            stage=ImportStage.scrape,
            code=ErrorCode.UPSTREAM_ERROR,
            http_status=502,
        ) from e

    logger.info("Apify actor run completed: %s", run.get("id"))

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        raise LinkedInImportAppError(
            "No dataset returned from Apify run",
            stage=ImportStage.scrape,
            code=ErrorCode.UPSTREAM_ERROR,
            http_status=502,
        )

    try:
        items_result = await client.dataset(dataset_id).list_items()
        items = items_result.items if items_result else []
    except LinkedInImportAppError:
        raise
    except ApifyApiError as e:
        logger.exception("Apify dataset fetch error: %s", e)
        raise LinkedInImportAppError(
            f"Error fetching dataset from Apify: {e}",
            stage=ImportStage.scrape,
            code=ErrorCode.UPSTREAM_ERROR,
            http_status=502,
        ) from e
    except Exception as e:
        logger.exception("Unexpected error fetching dataset")
        raise LinkedInImportAppError(
            f"Error fetching dataset: {e}",
            stage=ImportStage.scrape,
            code=ErrorCode.UPSTREAM_ERROR,
            http_status=502,
        ) from e

    if not items:
        raise LinkedInImportAppError(
            "No profile data returned from Apify",
            stage=ImportStage.scrape,
            code=ErrorCode.EMPTY_SCRAPE_RESULT,
            http_status=422,
        )

    result = items[0]
    if result.get("status") == "error":
        error_msg = result.get("error", "Unknown scraping error")
        raise LinkedInImportAppError(
            f"LinkedIn scraper could not access profile: {error_msg}",
            stage=ImportStage.scrape,
            code=ErrorCode.EMPTY_SCRAPE_RESULT,
            http_status=422,
        )

    logger.info("Apify scrape returned %d items", len(items))
    return result
