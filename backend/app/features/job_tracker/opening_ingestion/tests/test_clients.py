"""Targeted unit tests for apify_client and extraction_chain client behaviour."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.features.job_tracker.opening_ingestion.clients.apify_client import (
    CrawlError,
    crawl_url,
)
from app.features.job_tracker.opening_ingestion.clients.extraction_chain import (
    ExtractionError,
    extract_job_details,
)
from app.features.job_tracker.schemas import ExtractedJobDetails


# ---------------------------------------------------------------------------
# apify_client: content field selection and empty-content guard
# ---------------------------------------------------------------------------

def _make_dataset_page(items: list[dict]) -> MagicMock:
    page = MagicMock()
    page.items = items
    return page


@pytest.mark.asyncio
async def test_crawl_url_returns_text_when_present():
    """crawl_url returns the text field when it is non-empty."""
    item = {"url": "https://example.com", "text": "Job description here", "markdown": "# Job"}
    dataset_page = _make_dataset_page([item])

    mock_run = {"defaultDatasetId": "ds-abc"}
    mock_dataset = AsyncMock()
    mock_dataset.list_items = AsyncMock(return_value=dataset_page)
    mock_actor = AsyncMock()
    mock_actor.call = AsyncMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    with patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.ApifyClientAsync",
        return_value=mock_client,
    ), patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.get_settings",
        return_value=MagicMock(apify_api_token="test-token"),
    ):
        result = await crawl_url("https://example.com")

    assert result == "Job description here"


@pytest.mark.asyncio
async def test_crawl_url_falls_back_to_markdown_when_text_empty():
    """crawl_url falls back to markdown when text field is empty string."""
    item = {"url": "https://example.com", "text": "", "markdown": "# Real Content"}
    dataset_page = _make_dataset_page([item])

    mock_run = {"defaultDatasetId": "ds-abc"}
    mock_dataset = AsyncMock()
    mock_dataset.list_items = AsyncMock(return_value=dataset_page)
    mock_actor = AsyncMock()
    mock_actor.call = AsyncMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    with patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.ApifyClientAsync",
        return_value=mock_client,
    ), patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.get_settings",
        return_value=MagicMock(apify_api_token="test-token"),
    ):
        result = await crawl_url("https://example.com")

    assert result == "# Real Content"


@pytest.mark.asyncio
async def test_crawl_url_raises_when_both_text_and_markdown_empty():
    """crawl_url raises CrawlError when both text and markdown are empty strings."""
    item = {"url": "https://example.com", "text": "", "markdown": ""}
    dataset_page = _make_dataset_page([item])

    mock_run = {"defaultDatasetId": "ds-abc"}
    mock_dataset = AsyncMock()
    mock_dataset.list_items = AsyncMock(return_value=dataset_page)
    mock_actor = AsyncMock()
    mock_actor.call = AsyncMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    with patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.ApifyClientAsync",
        return_value=mock_client,
    ), patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.get_settings",
        return_value=MagicMock(apify_api_token="test-token"),
    ):
        with pytest.raises(CrawlError, match="No usable text content"):
            await crawl_url("https://example.com")


@pytest.mark.asyncio
async def test_crawl_url_raises_when_content_fields_absent():
    """crawl_url raises CrawlError when neither text nor markdown key is present."""
    item = {"url": "https://example.com", "title": "A Job"}
    dataset_page = _make_dataset_page([item])

    mock_run = {"defaultDatasetId": "ds-abc"}
    mock_dataset = AsyncMock()
    mock_dataset.list_items = AsyncMock(return_value=dataset_page)
    mock_actor = AsyncMock()
    mock_actor.call = AsyncMock(return_value=mock_run)

    mock_client = MagicMock()
    mock_client.actor = MagicMock(return_value=mock_actor)
    mock_client.dataset = MagicMock(return_value=mock_dataset)

    with patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.ApifyClientAsync",
        return_value=mock_client,
    ), patch(
        "app.features.job_tracker.opening_ingestion.clients.apify_client.get_settings",
        return_value=MagicMock(apify_api_token="test-token"),
    ):
        with pytest.raises(CrawlError, match="No usable text content"):
            await crawl_url("https://example.com")


# ---------------------------------------------------------------------------
# extraction_chain: source_url passed as template variable (not baked-in string)
# ---------------------------------------------------------------------------

SAMPLE_EXTRACTED = ExtractedJobDetails(
    job_title="Engineer",
    company_name="Acme",
    source_url="https://example.com/{job}/123",
)


@pytest.mark.asyncio
async def test_extract_job_details_source_url_with_braces_does_not_raise():
    """source_url containing {braces} is passed as a template variable, not baked into the
    template string, so LangChain does not try to resolve it as an input variable."""
    url_with_braces = "https://example.com/{job}/123"

    with patch(
        "app.features.job_tracker.opening_ingestion.clients.extraction_chain.configure_langsmith"
    ), patch(
        "app.features.job_tracker.opening_ingestion.clients.extraction_chain.get_chat_llm"
    ) as mock_llm_factory, patch(
        "app.features.job_tracker.agents.tracing.wrap_runnable"
    ) as mock_wrap:
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=SAMPLE_EXTRACTED)
        mock_wrap.return_value = mock_chain

        mock_llm = MagicMock()
        mock_llm.with_structured_output = MagicMock(return_value=MagicMock())
        mock_llm_factory.return_value = mock_llm

        result = await extract_job_details(
            "Job posting text",
            source_url=url_with_braces,
        )

    assert result == SAMPLE_EXTRACTED
    invoked_input = mock_chain.ainvoke.call_args[0][0]
    assert invoked_input["source_url"] == url_with_braces
    assert invoked_input["text"] == "Job posting text"


@pytest.mark.asyncio
async def test_extract_job_details_no_source_url_omits_source_url_variable():
    """When source_url is None, the invoke input contains only 'text'."""
    extracted = ExtractedJobDetails(job_title="Engineer")

    with patch(
        "app.features.job_tracker.opening_ingestion.clients.extraction_chain.configure_langsmith"
    ), patch(
        "app.features.job_tracker.opening_ingestion.clients.extraction_chain.get_chat_llm"
    ) as mock_llm_factory, patch(
        "app.features.job_tracker.agents.tracing.wrap_runnable"
    ) as mock_wrap:
        mock_chain = MagicMock()
        mock_chain.ainvoke = AsyncMock(return_value=extracted)
        mock_wrap.return_value = mock_chain

        mock_llm = MagicMock()
        mock_llm.with_structured_output = MagicMock(return_value=MagicMock())
        mock_llm_factory.return_value = mock_llm

        result = await extract_job_details("Job posting text", source_url=None)

    assert result == extracted
    invoked_input = mock_chain.ainvoke.call_args[0][0]
    assert "source_url" not in invoked_input
    assert invoked_input["text"] == "Job posting text"
