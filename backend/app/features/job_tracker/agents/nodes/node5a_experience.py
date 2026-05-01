"""Node 5a: Tailor experience section using XYZ bullet format."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_experience(state: AgentState) -> dict[str, Any]:
    """Rewrite experience entries to match job requirements using XYZ format."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt, load_skill
    from app.features.job_tracker.opening_resume.experience.service import (
        list_entries, update_entry,
    )
    from app.features.job_tracker.opening_resume.experience.schemas import ExperienceUpdate
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        entries = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
        if not entries:
            return {
                "experience_tailored": True,
                "events": events + [{
                    "node": "experience",
                    "status": "completed",
                    "message": "No experience entries to tailor",
                }],
            }

        extracted = state.get("extracted_details", {})
        system_prompt = load_prompt("node_5a_experience")
        bullet_skill = load_skill("refine_bullet_point")
        full_system = system_prompt + "\n\n## Bullet Point Skill Reference\n" + bullet_skill

        llm = get_chat_llm(temperature=0.3)

        for entry in entries:
            entry_dict = dict(entry)
            extracted_str = json.dumps({
                "job_title": extracted.get("job_title"),
                "required_skills": extracted.get("required_skills"),
                "role_summary": extracted.get("role_summary"),
                "technical_keywords": extracted.get("technical_keywords"),
            }, default=str)
            entry_str = json.dumps({
                "title": entry_dict.get("title"),
                "company": entry_dict.get("company"),
                "description": entry_dict.get("description"),
            }, default=str)
            human_msg = (
                f"Job details:\n{extracted_str}\n\n"
                f"Current experience entry:\n{entry_str}\n\n"
                "Rewrite the description field using XYZ bullet format. "
                "Return ONLY the rewritten description text, nothing else."
            )
            result = await ainvoke_with_retry(llm, [
                SystemMessage(content=full_system),
                HumanMessage(content=human_msg),
            ])

            new_description = result.content.strip()
            if new_description and new_description != entry_dict.get("description"):
                update_data = ExperienceUpdate(description=new_description)
                await update_entry(
                    ctx.conn, ctx.user_id, ctx.opening_id,
                    entry_dict["id"], update_data,
                )

        return {
            "experience_tailored": True,
            "events": events + [{
                "node": "experience",
                "status": "completed",
                "message": f"Tailored {len(entries)} experience entries",
            }],
        }
    except Exception as e:
        return {
            "experience_tailored": False,
            "error": f"Experience tailoring failed: {e}",
            "events": events + [{
                "node": "experience",
                "status": "error",
                "message": str(e),
            }],
        }
