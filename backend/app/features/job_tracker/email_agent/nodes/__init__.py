"""Email agent node exports."""
from __future__ import annotations

from langchain_core.messages import SystemMessage, HumanMessage
from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry


async def _chat(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    llm = get_chat_llm(max_tokens=max_tokens)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    response = await ainvoke_with_retry(llm, messages)
    return response.content.strip()


from app.features.job_tracker.email_agent.nodes.jd_parser import jd_parser
from app.features.job_tracker.email_agent.nodes.resume_extractor import resume_extractor
from app.features.job_tracker.email_agent.nodes.contact_lookup import contact_lookup
from app.features.job_tracker.email_agent.nodes.linkedin_input import linkedin_input
from app.features.job_tracker.email_agent.nodes.email_generator import email_generator
from app.features.job_tracker.email_agent.nodes.subject_generator import subject_generator
from app.features.job_tracker.email_agent.nodes.export_node import export_node

__all__ = [
    "jd_parser",
    "resume_extractor",
    "contact_lookup",
    "linkedin_input",
    "email_generator",
    "subject_generator",
    "export_node",
]
