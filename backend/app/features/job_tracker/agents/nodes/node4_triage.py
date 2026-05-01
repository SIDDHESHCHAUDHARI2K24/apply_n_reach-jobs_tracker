"""Node 4: Triage — analyze which resume sections need modification."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_triage(state: AgentState) -> dict[str, Any]:
    """Analyze current resume sections vs extracted job details.

    Produces a triage plan indicating what needs to change in each section.
    """
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        # Gather current resume state
        from app.features.job_tracker.opening_resume.personal.service import get_personal
        from app.features.job_tracker.opening_resume.education.service import list_entries as list_edu
        from app.features.job_tracker.opening_resume.experience.service import list_entries as list_exp
        from app.features.job_tracker.opening_resume.projects.service import list_entries as list_proj
        from app.features.job_tracker.opening_resume.skills.service import list_entries as list_skills

        personal = await get_personal(ctx.conn, ctx.user_id, ctx.opening_id)
        education = await list_edu(ctx.conn, ctx.user_id, ctx.opening_id)
        experience = await list_exp(ctx.conn, ctx.user_id, ctx.opening_id)
        projects = await list_proj(ctx.conn, ctx.user_id, ctx.opening_id)
        skills = await list_skills(ctx.conn, ctx.user_id, ctx.opening_id)

        extracted = state.get("extracted_details", {})

        resume_summary = {
            "personal": dict(personal) if personal else {},
            "education_count": len(education),
            "experience_count": len(experience),
            "experience_titles": [dict(e).get("title", "") for e in experience],
            "projects_count": len(projects),
            "skills_count": len(skills),
            "skills_list": [dict(s).get("name", "") for s in skills],
        }

        system_prompt = load_prompt("node_4_triage")
        llm = get_chat_llm(temperature=0)

        extracted_str = json.dumps(extracted, default=str)[:4000]
        resume_str = json.dumps(resume_summary, default=str)[:2000]
        human_msg = (
            f"Extracted job details:\n{extracted_str}\n\n"
            f"Current resume state:\n{resume_str}\n\n"
            "Produce a triage plan as JSON with keys: experience, projects, skills, personal, certifications. "
            "Each key should have: action (keep/modify/rewrite), priority (high/medium/low), notes (string)."
        )

        result = await ainvoke_with_retry(llm, [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_msg),
        ])

        # Try to parse JSON from the response
        content = result.content.strip()
        # Extract JSON from markdown code blocks if present
        if "```" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                content = content[start:end]
        try:
            triage = json.loads(content)
        except json.JSONDecodeError:
            triage = {
                "experience": {"action": "modify", "priority": "high", "notes": "Default triage"},
                "projects": {"action": "modify", "priority": "medium", "notes": "Default triage"},
                "skills": {"action": "modify", "priority": "high", "notes": "Default triage"},
                "personal": {"action": "modify", "priority": "medium", "notes": "Default triage"},
                "certifications": {"action": "keep", "priority": "low", "notes": "Default triage"},
            }

        return {
            "triage": triage,
            "events": events + [{
                "node": "triage",
                "status": "completed",
                "message": "Triage plan created",
                "data": triage,
            }],
        }
    except Exception as e:
        return {
            "triage": {},
            "error": f"Triage failed: {e}",
            "events": events + [{
                "node": "triage",
                "status": "error",
                "message": str(e),
            }],
        }
