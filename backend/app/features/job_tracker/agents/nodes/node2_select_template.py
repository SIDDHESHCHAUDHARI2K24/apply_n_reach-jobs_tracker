"""Node 2: Select the best-matching job profile as template."""
from __future__ import annotations

from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_select_template(state: AgentState) -> dict[str, Any]:
    """Select the best job_profile to use as a resume template.

    Queries all user's job_profiles and picks the one whose target_role
    best matches the extracted job details. If only one profile exists,
    selects it automatically.
    """
    from app.features.job_tracker.agents.mcp_server import get_context

    ctx = get_context()
    events = list(state.get("events", []))

    try:
        # Get all user's job profiles
        profiles = await ctx.conn.fetch(
            "SELECT id, profile_name, target_role, summary FROM job_profiles WHERE user_id=$1 ORDER BY id",
            ctx.user_id,
        )

        if not profiles:
            return {
                "error": "No job profiles found. Create a job profile first.",
                "events": events + [{
                    "node": "select_template",
                    "status": "error",
                    "message": "No job profiles available",
                }],
            }

        # If only one profile, use it
        if len(profiles) == 1:
            selected_id = profiles[0]["id"]
        else:
            # Use LLM to pick the best match
            extracted = state.get("extracted_details", {})
            job_title = extracted.get("job_title", "Unknown")
            required_skills = extracted.get("required_skills", [])

            from app.features.job_tracker.agents.llm_factory import get_chat_llm, ainvoke_with_retry
            from langchain_core.messages import SystemMessage, HumanMessage

            profile_descriptions = "\n".join(
                f"- ID {p['id']}: {p['profile_name']} (target: {p['target_role']})"
                for p in profiles
            )

            llm = get_chat_llm(temperature=0)
            result = await ainvoke_with_retry(llm, [
                SystemMessage(content=(
                    "You are selecting the best job profile template for a resume. "
                    "Return ONLY the numeric ID of the best matching profile."
                )),
                HumanMessage(content=(
                    f"Job: {job_title}\nSkills needed: {', '.join(required_skills or [])}\n\n"
                    f"Available profiles:\n{profile_descriptions}\n\n"
                    "Which profile ID is the best match? Reply with just the number."
                )),
            ])
            # Parse the ID from the response
            try:
                selected_id = int(result.content.strip())
                # Validate it's a real profile
                valid_ids = {p["id"] for p in profiles}
                if selected_id not in valid_ids:
                    selected_id = profiles[0]["id"]
            except (ValueError, AttributeError):
                selected_id = profiles[0]["id"]

        selected_name = next(
            (p["profile_name"] for p in profiles if p["id"] == selected_id),
            "Unknown",
        )

        return {
            "selected_job_profile_id": selected_id,
            "events": events + [{
                "node": "select_template",
                "status": "completed",
                "message": f"Selected profile '{selected_name}' (ID: {selected_id})",
            }],
        }
    except Exception as e:
        return {
            "error": f"Template selection failed: {e}",
            "events": events + [{
                "node": "select_template",
                "status": "error",
                "message": str(e),
            }],
        }
