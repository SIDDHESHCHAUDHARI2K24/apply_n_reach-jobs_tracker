"""Node 8: Content optimiser — trim or expand to hit 1-page target."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState

MAX_OPTIMISER_ITERATIONS = 3


async def node_optimiser(state: AgentState) -> dict[str, Any]:
    """Trim content if >1 page, expand if <0.7 pages. Then re-render."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt
    from app.features.job_tracker.opening_resume.experience.service import (
        list_entries as list_exp, update_entry as update_exp,
    )
    from app.features.job_tracker.opening_resume.experience.schemas import ExperienceUpdate
    from app.features.job_tracker.opening_resume.projects.service import (
        list_entries as list_proj, update_entry as update_proj, delete_entry as delete_proj,
    )
    from app.features.job_tracker.opening_resume.projects.schemas import ProjectUpdate
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))
    iterations = state.get("optimiser_iterations", 0) + 1
    page_count = state.get("pdf_page_count", 1)

    try:
        system_prompt = load_prompt("node_8_optimiser")
        llm = get_chat_llm(temperature=0.2)

        if page_count > 1:
            # TRIM: shorten descriptions, remove least relevant projects
            experiences = await list_exp(ctx.conn, ctx.user_id, ctx.opening_id)
            projects = await list_proj(ctx.conn, ctx.user_id, ctx.opening_id)

            # Ask LLM what to trim
            exp_str = json.dumps([
                {"id": dict(e)["id"], "title": dict(e).get("title"), "description": dict(e).get("description")}
                for e in experiences
            ], default=str)
            proj_str = json.dumps([
                {"id": dict(p)["id"], "name": dict(p).get("name"), "description": dict(p).get("description")}
                for p in projects
            ], default=str)
            human_msg = (
                f"The resume is {page_count} pages. Target is 1 page.\n\n"
                f"Experience entries:\n{exp_str}\n\n"
                f"Project entries:\n{proj_str}\n\n"
                "Return JSON with:\n"
                '- "trim_experiences": list of {"id": N, "shorter_description": "..."} to shorten\n'
                '- "remove_project_ids": list of project IDs to remove entirely\n'
                "Focus on removing the least relevant content first."
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
                changes = {}

            # Apply trims
            for trim in changes.get("trim_experiences", []):
                if isinstance(trim, dict) and "id" in trim and "shorter_description" in trim:
                    await update_exp(
                        ctx.conn, ctx.user_id, ctx.opening_id,
                        trim["id"], ExperienceUpdate(description=trim["shorter_description"]),
                    )

            for proj_id in changes.get("remove_project_ids", []):
                try:
                    await delete_proj(ctx.conn, ctx.user_id, ctx.opening_id, proj_id)
                except Exception:
                    pass  # May already be deleted

            action = "trimmed"
        else:
            # Page count is OK (1 page) — no changes needed
            action = "no_change"

        return {
            "optimiser_iterations": iterations,
            "events": events + [{
                "node": "optimiser",
                "status": "completed",
                "message": f"Optimiser iteration {iterations}: {action} (was {page_count} pages)",
            }],
        }
    except Exception as e:
        return {
            "optimiser_iterations": iterations,
            "events": events + [{
                "node": "optimiser",
                "status": "error",
                "message": str(e),
            }],
        }


def should_continue_optimising(state: AgentState) -> str:
    """Conditional edge: re-render or end based on page count and iterations."""
    page_count = state.get("pdf_page_count", 1)
    iterations = state.get("optimiser_iterations", 0)

    if page_count == 1 or iterations >= MAX_OPTIMISER_ITERATIONS:
        return "end"
    return "render"
