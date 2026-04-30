"""LangChain extraction chain for structured job detail extraction."""
import json

from app.features.job_tracker.schemas import ExtractedJobDetails
from app.features.job_tracker.agents.llm_factory import get_chat_llm
from app.features.job_tracker.agents.config import DEFAULT_MODEL


class ExtractionError(Exception):
    pass


async def extract_job_details(raw_text: str) -> ExtractedJobDetails:
    """Extract structured job details from raw page text using LangChain + OpenRouter.

    Returns ExtractedJobDetails. Raises ExtractionError on failure.
    """
    try:
        model = get_chat_llm(temperature=0).with_structured_output(ExtractedJobDetails)

        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "Extract structured job posting information from the provided text. "
                "Return only fields you are confident about; leave others as null. "
                "For role_summary, write a 2-3 sentence summary of the role. "
                "For technical_keywords, list specific technologies, languages, frameworks mentioned. "
                "For sector_keywords, list industry/domain terms. "
                "For business_sectors, list the industries this role serves. "
                "For problem_being_solved, describe what business problem this role addresses. "
                "For useful_experiences, list specific past experiences that would be valuable.",
            ),
            ("human", "{text}"),
        ])

        chain = prompt | model
        result = await chain.ainvoke({"text": raw_text[:8000]})

        if not isinstance(result, ExtractedJobDetails):
            raise ExtractionError(f"Unexpected extraction result type: {type(result)}")
        result.extractor_model = DEFAULT_MODEL
        return result
    except ExtractionError:
        raise
    except Exception as e:
        raise ExtractionError(f"Extraction failed: {e}") from e
