"""LangChain + Claude extraction chain for structured job detail extraction."""
import json

from app.features.job_tracker.schemas import ExtractedJobDetails
from app.features.core.config import get_settings

EXTRACTION_MODEL = "claude-haiku-4-5-20251001"


class ExtractionError(Exception):
    pass


async def extract_job_details(raw_text: str) -> ExtractedJobDetails:
    """Extract structured job details from raw page text using LangChain + Claude.

    Returns ExtractedJobDetails. Raises ExtractionError on failure.
    Uses settings.anthropic_api_key.
    """
    settings = get_settings()
    api_key = getattr(settings, "anthropic_api_key", None)
    if not api_key:
        raise ExtractionError("Anthropic API key not configured")

    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.prompts import ChatPromptTemplate

        model = ChatAnthropic(
            model=EXTRACTION_MODEL,
            api_key=api_key,
            temperature=0,
        ).with_structured_output(ExtractedJobDetails)

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Extract structured job posting information from the provided text. "
                "Return only fields you are confident about; leave others as null.",
            ),
            ("human", "{text}"),
        ])

        chain = prompt | model
        result = await chain.ainvoke({"text": raw_text[:8000]})

        if not isinstance(result, ExtractedJobDetails):
            raise ExtractionError(f"Unexpected extraction result type: {type(result)}")
        return result
    except ExtractionError:
        raise
    except Exception as e:
        raise ExtractionError(f"Extraction failed: {e}") from e
