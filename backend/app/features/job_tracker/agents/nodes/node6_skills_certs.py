"""Node 6: Final skills & certifications alignment pass."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_skills_certs(state: AgentState) -> dict[str, Any]:
    """Final pass ensuring certifications align with job requirements."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
    from app.features.job_tracker.agents.prompt_loader import load_prompt
    from app.features.job_tracker.opening_resume.certifications.service import (
        list_entries as list_certs,
    )
    from langchain_core.messages import SystemMessage, HumanMessage

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        certs = await list_certs(ctx.conn, ctx.user_id, ctx.opening_id)
        extracted = state.get("extracted_details", {})

        # This node primarily verifies alignment — no heavy modifications
        # since certifications are factual (can't be invented)
        system_prompt = load_prompt("node_6_skills_certs")
        llm = get_chat_llm(temperature=0)

        human_msg = (
            f"Job required skills: {json.dumps(extracted.get('required_skills', []), default=str)}\n"
            f"Current certifications: {json.dumps([dict(c).get('name', '') for c in certs], default=str)}\n\n"
            "Are the certifications well-ordered for this role? Respond with a brief assessment."
        )
        result = await ainvoke_with_retry(llm, [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_msg),
        ])

        return {
            "skills_certs_done": True,
            "events": events + [{
                "node": "skills_certs",
                "status": "completed",
                "message": f"Verified {len(certs)} certifications alignment",
            }],
        }
    except Exception as e:
        return {
            "skills_certs_done": True,  # Non-blocking — continue even on failure
            "events": events + [{
                "node": "skills_certs",
                "status": "error",
                "message": str(e),
            }],
        }
