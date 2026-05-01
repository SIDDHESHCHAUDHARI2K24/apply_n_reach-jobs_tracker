"""Node 3: Create opening resume snapshot from selected job profile."""
from __future__ import annotations

from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_snapshot(state: AgentState) -> dict[str, Any]:
    """Create an opening resume by snapshotting the selected job profile."""
    from app.features.job_tracker.agents.mcp_server import get_context
    from app.features.job_tracker.opening_resume.service import create_opening_resume

    ctx = get_context()
    events = list(state.get("events", []))
    profile_id = state.get("selected_job_profile_id")

    if not profile_id:
        return {
            "error": "No job profile selected",
            "events": events + [{
                "node": "snapshot",
                "status": "error",
                "message": "No job profile selected for snapshot",
            }],
        }

    try:
        # Check if resume already exists
        existing = await ctx.conn.fetchrow(
            """
            SELECT r.id FROM job_opening_resumes r
            JOIN job_openings o ON o.id = r.opening_id
            WHERE r.opening_id=$1 AND o.user_id=$2
            """,
            ctx.opening_id, ctx.user_id,
        )

        if existing:
            return {
                "resume_created": True,
                "events": events + [{
                    "node": "snapshot",
                    "status": "completed",
                    "message": "Resume already exists, proceeding with existing snapshot",
                }],
            }

        await create_opening_resume(ctx.conn, ctx.user_id, ctx.opening_id, profile_id)

        return {
            "resume_created": True,
            "events": events + [{
                "node": "snapshot",
                "status": "completed",
                "message": f"Created resume snapshot from profile {profile_id}",
            }],
        }
    except Exception as e:
        return {
            "error": f"Snapshot creation failed: {e}",
            "events": events + [{
                "node": "snapshot",
                "status": "error",
                "message": str(e),
            }],
        }
