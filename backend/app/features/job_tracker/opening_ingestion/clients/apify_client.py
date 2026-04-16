"""Apify website-content-crawler client for job posting ingestion."""
import httpx
from app.features.core.config import get_settings


class CrawlError(Exception):
    pass


async def crawl_url(url: str) -> str:
    """Crawl a URL using Apify website-content-crawler actor.

    Returns raw text content. Raises CrawlError on failure.

    Uses settings.apify_api_token. If token not configured, raises
    CrawlError("Apify API token not configured").
    """
    settings = get_settings()
    token = getattr(settings, "apify_api_token", None)
    if not token:
        raise CrawlError("Apify API token not configured")

    actor_id = "apify/website-content-crawler"
    endpoint = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                endpoint,
                params={"token": token},
                json={
                    "startUrls": [{"url": url}],
                    "maxCrawlPages": 1,
                    "crawlerType": "cheerio",
                },
            )
            response.raise_for_status()
            items = response.json()
            if not items:
                raise CrawlError(f"No content returned for URL: {url}")
            return items[0].get("text", items[0].get("markdown", ""))
        except httpx.HTTPError as e:
            raise CrawlError(f"HTTP error crawling {url}: {e}") from e
