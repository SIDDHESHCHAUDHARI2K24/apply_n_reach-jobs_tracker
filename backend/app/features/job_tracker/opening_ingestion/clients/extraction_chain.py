"""LangChain extraction chain for structured job detail extraction."""
from __future__ import annotations

from typing import Any

from app.features.job_tracker.schemas import ExtractedJobDetails
from app.features.job_tracker.agents.config import DEFAULT_MODEL, configure_langsmith
from app.features.job_tracker.agents.llm_factory import get_chat_llm


class ExtractionError(Exception):
    pass


async def extract_job_details(
    raw_text: str,
    *,
    source_url: str | None = None,
    opening_id: int | None = None,
    run_id: int | None = None,
    trace_metadata: dict[str, Any] | None = None,
) -> ExtractedJobDetails:
    """Extract structured job details from raw page text using LangChain + OpenAI.

    ``source_url``, when provided, is included in the prompt so the model can
    populate the source_url field and use it as context for extraction.

    When ``LANGCHAIN_API_KEY`` is set, configures LangSmith tracing and tags the
    chain as ``job_opening_extraction`` (tags: opening_ingestion, extraction).

    Returns ExtractedJobDetails. Raises ExtractionError on failure.
    """
    try:
        configure_langsmith()

        from langchain_core.prompts import ChatPromptTemplate
        from app.features.job_tracker.agents.tracing import wrap_runnable

        llm_base = get_chat_llm(temperature=0)
        model = llm_base.with_structured_output(ExtractedJobDetails)

        url_context = f"\nSource URL: {source_url}" if source_url else ""
        human_template = "{text}" + url_context

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Extract structured job posting information from the provided text. "
                "Return only fields you are confident about; leave others as null. "
                "Do not extract salary, compensation, or perks as a separate field — if the posting "
                "mentions pay or benefits, weave that context naturally into description_summary or role_summary. "
                "For role_summary, write a 2-3 sentence summary of the role. "
                "For technical_keywords, list specific technologies, languages, frameworks mentioned. "
                "For sector_keywords, list industry/domain terms. "
                "For business_sectors, list the industries this role serves. "
                "For problem_being_solved, describe what business problem this role addresses. "
                "For useful_experiences, list specific past experiences that would be valuable. "
                "If a Source URL is provided, populate the source_url field with it exactly.",
            ),
            ("human", human_template),
        ])

        metadata: dict[str, Any] = dict(trace_metadata or {})
        if opening_id is not None:
            metadata["opening_id"] = opening_id
        if run_id is not None:
            metadata["run_id"] = run_id
        if source_url is not None:
            metadata["source_url"] = source_url

        base_chain = prompt | model
        chain = wrap_runnable(
            base_chain,
            name="job_opening_extraction",
            tags=["opening_ingestion", "extraction"],
            metadata=metadata,
        )

        result = await chain.ainvoke({"text": raw_text[:8000]})

        if not isinstance(result, ExtractedJobDetails):
            raise ExtractionError(f"Unexpected extraction result type: {type(result)}")
        result.extractor_model = getattr(llm_base, "model_name", DEFAULT_MODEL)
        if source_url and not result.source_url:
            result.source_url = source_url
        return result
    except ExtractionError:
        raise
    except Exception as e:
        raise ExtractionError(f"Extraction failed: {e}") from e
