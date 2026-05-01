"""Node 1: Extract job details from the opening's extracted data."""
from __future__ import annotations

import json
from typing import Any

from app.features.job_tracker.agents.state import AgentState


async def node_extract(state: AgentState) -> dict[str, Any]:
    """Load extracted details from DB into agent state.

    This node reads the pre-extracted job details (from the ingestion pipeline)
    rather than re-extracting. If no extraction exists, it signals an error.
    """
    from app.features.job_tracker.agents.mcp_server import get_context

    ctx = get_context()
    from app.features.job_tracker.opening_ingestion.service import get_latest_extracted_details

    try:
        row = await get_latest_extracted_details(ctx.conn, ctx.user_id, ctx.opening_id)
        details = dict(row)
        # Parse JSONB string fields
        for key in ("required_skills", "preferred_skills", "technical_keywords",
                     "sector_keywords", "business_sectors", "useful_experiences", "raw_payload"):
            val = details.get(key)
            if isinstance(val, str):
                try:
                    details[key] = json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    pass

        return {
            "extracted_details": details,
            "events": state.get("events", []) + [{
                "node": "extract",
                "status": "completed",
                "message": f"Loaded extracted details for opening {ctx.opening_id}",
            }],
        }
    except Exception as e:
        return {
            "error": f"Extraction load failed: {e}",
            "events": state.get("events", []) + [{
                "node": "extract",
                "status": "error",
                "message": str(e),
            }],
        }
