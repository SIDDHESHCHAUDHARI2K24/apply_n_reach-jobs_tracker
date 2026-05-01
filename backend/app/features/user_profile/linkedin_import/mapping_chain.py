"""LLM chain to map raw LinkedIn data to user_profile schema.

Mapping expectations and examples are documented in:
`linkedin_mapping_skill.md`.
"""
import json
import logging

from app.features.job_tracker.agents.llm_factory import get_chat_llm
from app.features.user_profile.linkedin_import.schemas import MappedLinkedInProfile
from app.features.user_profile.linkedin_import.errors import (
    ErrorCode,
    ImportStage,
    LinkedInImportAppError,
)

logger = logging.getLogger(__name__)


async def map_linkedin_to_profile(raw_data: dict) -> MappedLinkedInProfile:
    """Map raw LinkedIn scrape data to MappedLinkedInProfile via LLM structured output.

    Returns MappedLinkedInProfile. Raises LinkedInImportAppError on failure.
    """
    logger.info("Starting LinkedIn profile mapping (keys=%s)", list(raw_data.keys())[:10])
    try:
        model = get_chat_llm(temperature=0).with_structured_output(MappedLinkedInProfile)

        from langchain_core.messages import SystemMessage
        from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
        from app.features.job_tracker.agents.prompt_loader import load_prompt

        system_prompt = load_prompt("linkedin_map")

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            HumanMessagePromptTemplate.from_template(
                "Map this LinkedIn profile data to the structured format:\n\n{data}",
            ),
        ])

        chain = prompt | model
        result = await chain.ainvoke({"data": json.dumps(raw_data, indent=2)[:12000]})

        if not isinstance(result, MappedLinkedInProfile):
            raise LinkedInImportAppError(
                f"Unexpected mapping result type: {type(result)}",
                stage=ImportStage.map,
                code=ErrorCode.UNEXPECTED_RESULT,
                http_status=424,
            )
        logger.info("LinkedIn profile mapping completed successfully")
        return result
    except LinkedInImportAppError:
        raise
    except Exception as e:
        logger.exception("LinkedIn mapping failed")
        raise LinkedInImportAppError(
            f"LinkedIn mapping failed: {e}",
            stage=ImportStage.map,
            code=ErrorCode.LLM_FAILURE,
            http_status=424,
        ) from e
