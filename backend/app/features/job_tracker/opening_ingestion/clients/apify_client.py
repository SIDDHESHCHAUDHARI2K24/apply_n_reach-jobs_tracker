"""Apify website-content-crawler client for job posting ingestion."""
from apify_client import ApifyClientAsync
from apify_client.errors import ApifyApiError

from app.features.core.config import get_settings

ACTOR_ID = "apify~website-content-crawler"


class CrawlError(Exception):
    pass


async def crawl_url(url: str) -> str:
    """Crawl a URL using Apify website-content-crawler actor.

    Uses Playwright (Chrome) for full JavaScript rendering so modern job
    boards (Greenhouse, Lever, LinkedIn, etc.) are scraped correctly.
    Returns raw text content. Raises CrawlError on failure.
    """
    settings = get_settings()
    token = getattr(settings, "apify_api_token", None)
    if not token:
        raise CrawlError("Apify API token not configured")

    client = ApifyClientAsync(token=token)
    try:
        run = await client.actor(ACTOR_ID).call(
            run_input={
                "startUrls": [{"url": url}],
                "maxCrawlPages": 1,
                "crawlerType": "playwright:chrome",
            },
            wait_secs=60,
        )
    except ApifyApiError as e:
        raise CrawlError(f"Apify API error crawling {url}: {e}") from e
    except Exception as e:
        raise CrawlError(f"Error calling Apify for {url}: {e}") from e

    dataset_id = run.get("defaultDatasetId") if run else None
    if not dataset_id:
        raise CrawlError(f"No dataset returned from Apify for {url}")

    try:
        items_result = await client.dataset(dataset_id).list_items()
        items = items_result.items if items_result else []
    except Exception as e:
        raise CrawlError(f"Error fetching Apify dataset for {url}: {e}") from e

    if not items:
        raise CrawlError(f"No content returned for URL: {url}")

    content = items[0].get("text") or items[0].get("markdown") or ""
    if not content.strip():
        raise CrawlError(f"No usable text content extracted from URL: {url}")
    return content
