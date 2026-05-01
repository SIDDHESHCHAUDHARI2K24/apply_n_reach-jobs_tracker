"""Node 5c: Optimize skills section to match job requirements."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_skills(state: AgentState) -> dict[str, Any]:
    """Add missing required/preferred skills, remove irrelevant ones, reorder."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt
    from app.features.job_tracker.opening_resume.skills.service import (
        list_entries, create_entry, delete_entry,
    )
    from app.features.job_tracker.opening_resume.skills.schemas import SkillCreate
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        current_skills = await list_entries(ctx.conn, ctx.user_id, ctx.opening_id)
        current_names = {dict(s)["name"].lower() for s in current_skills}

        extracted = state.get("extracted_details", {})
        required = extracted.get("required_skills") or []
        preferred = extracted.get("preferred_skills") or []
        technical_kw = extracted.get("technical_keywords") or []

        system_prompt = load_prompt("node_5c_skills")
        llm = get_chat_llm(temperature=0)

        human_msg = (
            f"Job required skills: {json.dumps(required)}\n"
            f"Job preferred skills: {json.dumps(preferred)}\n"
            f"Technical keywords: {json.dumps(technical_kw)}\n\n"
            f"Current resume skills: {json.dumps([dict(s)['name'] for s in current_skills])}\n\n"
            'Return JSON with two arrays:\n'
            '- "add": skills to add (from required/preferred that are missing)\n'
            '- "remove": skills to remove (irrelevant to this role)\n'
            "Only include skills the candidate plausibly has based on their resume context."
        )
        result = await ainvoke_with_retry(llm, [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_msg),
        ])

        content = result.content.strip()
        if "```" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                content = content[start:end]

        try:
            changes = json.loads(content)
        except json.JSONDecodeError:
            changes = {"add": [], "remove": []}

        # Apply additions
        added = 0
        for skill_name in changes.get("add", []):
            if skill_name.lower() not in current_names:
                await create_entry(
                    ctx.conn, ctx.user_id, ctx.opening_id,
                    SkillCreate(category="technical", name=skill_name, display_order=added + len(current_skills)),
                )
                current_names.add(skill_name.lower())
                added += 1

        # Apply removals
        removed = 0
        remove_names = {n.lower() for n in changes.get("remove", [])}
        for skill in current_skills:
            if dict(skill)["name"].lower() in remove_names:
                await delete_entry(ctx.conn, ctx.user_id, ctx.opening_id, dict(skill)["id"])
                removed += 1

        return {
            "skills_tailored": True,
            "events": events + [{
                "node": "skills",
                "status": "completed",
                "message": f"Added {added} skills, removed {removed}",
            }],
        }
    except Exception as e:
        return {
            "skills_tailored": False,
            "error": f"Skills optimization failed: {e}",
            "events": events + [{
                "node": "skills",
                "status": "error",
                "message": str(e),
            }],
        }
