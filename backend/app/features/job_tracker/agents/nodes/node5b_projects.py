"""Node 5b: Tailor projects section for relevance to target role."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_projects(state: AgentState) -> dict[str, Any]:
    """Rewrite project descriptions to highlight relevance to the target role."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt
    from app.features.job_tracker.opening_resume.projects.service import (
        list_entries, update_entry,
    )
    from app.features.job_tracker.opening_resume.projects.schemas import ProjectUpdate
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        entries = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
        if not entries:
            return {
                "projects_tailored": True,
                "events": events + [{
                    "node": "projects",
                    "status": "completed",
                    "message": "No project entries to tailor",
                }],
            }

        extracted = state.get("extracted_details", {})
        system_prompt = load_prompt("node_5b_projects")
        llm = get_chat_llm(temperature=0.3)

        for entry in entries:
            entry_dict = dict(entry)
            extracted_str = json.dumps({
                "job_title": extracted.get("job_title"),
                "required_skills": extracted.get("required_skills"),
                "technical_keywords": extracted.get("technical_keywords"),
            }, default=str)
            entry_str = json.dumps({
                "name": entry_dict.get("name"),
                "description": entry_dict.get("description"),
            }, default=str)
            human_msg = (
                f"Job details:\n{extracted_str}\n\n"
                f"Current project:\n{entry_str}\n\n"
                "Rewrite the description to emphasize relevance to the target role. "
                "Return ONLY the rewritten description text."
            )
            result = await ainvoke_with_retry(llm, [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_msg),
            ])

            new_description = result.content.strip()
            if new_description and new_description != entry_dict.get("description"):
                update_data = ProjectUpdate(description=new_description)
                await update_entry(
                    ctx.conn, ctx.user_id, ctx.opening_id,
                    entry_dict["id"], update_data,
                )

        return {
            "projects_tailored": True,
            "events": events + [{
                "node": "projects",
                "status": "completed",
                "message": f"Tailored {len(entries)} project entries",
            }],
        }
    except Exception as e:
        return {
            "projects_tailored": False,
            "error": f"Projects tailoring failed: {e}",
            "events": events + [{
                "node": "projects",
                "status": "error",
                "message": str(e),
            }],
        }
