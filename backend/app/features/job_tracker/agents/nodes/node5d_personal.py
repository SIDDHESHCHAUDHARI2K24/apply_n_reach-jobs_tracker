"""Node 5d: Tailor personal/summary section for the target role."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_personal(state: AgentState) -> dict[str, Any]:
    """Write a targeted professional summary for the personal section."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt
    from app.features.job_tracker.opening_resume.personal.service import (
        get_personal, upsert_personal,
    )
    from app.features.job_tracker.opening_resume.personal.schemas import PersonalUpdate
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        personal = await get_personal(ctx.conn, ctx.user_id, ctx.opening_id)
        personal_dict = dict(personal) if personal else {}

        extracted = state.get("extracted_details", {})
        system_prompt = load_prompt("node_5d_personal")
        llm = get_chat_llm(temperature=0.3)

        extracted_str = json.dumps({
            "job_title": extracted.get("job_title"),
            "company_name": extracted.get("company_name"),
            "role_summary": extracted.get("role_summary"),
            "required_skills": extracted.get("required_skills"),
        }, default=str)
        personal_str = json.dumps({
            "full_name": personal_dict.get("full_name"),
            "summary": personal_dict.get("summary"),
        }, default=str)
        human_msg = (
            f"Job details:\n{extracted_str}\n\n"
            f"Current personal section:\n{personal_str}\n\n"
            "Write a 2-3 sentence professional summary tailored for this role. "
            "Return ONLY the summary text."
        )
        result = await ainvoke_with_retry(llm, [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_msg),
        ])

        new_summary = result.content.strip()
        if new_summary:
            update_data = PersonalUpdate(
                full_name=personal_dict.get("full_name"),
                email=personal_dict.get("email"),
                phone=personal_dict.get("phone"),
                location=personal_dict.get("location"),
                linkedin_url=personal_dict.get("linkedin_url"),
                github_url=personal_dict.get("github_url"),
                portfolio_url=personal_dict.get("portfolio_url"),
                summary=new_summary,
            )
            await upsert_personal(ctx.conn, ctx.user_id, ctx.opening_id, update_data)

        return {
            "personal_tailored": True,
            "events": events + [{
                "node": "personal",
                "status": "completed",
                "message": "Updated professional summary",
            }],
        }
    except Exception as e:
        return {
            "personal_tailored": False,
            "error": f"Personal tailoring failed: {e}",
            "events": events + [{
                "node": "personal",
                "status": "error",
                "message": str(e),
            }],
        }
