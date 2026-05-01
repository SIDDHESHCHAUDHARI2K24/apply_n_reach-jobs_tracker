"""Service layer for email agent run persistence."""
from __future__ import annotations

import json
from typing import Any

import asyncpg


async def create_email_agent_run(
    conn: asyncpg.Connection, opening_id: int, user_id: int,
) -> int:
    """Insert a new email agent run row and return its ID."""
    row = await conn.fetchrow(
        """
        INSERT INTO job_opening_email_agent_runs (opening_id, user_id, status)
        VALUES ($1, $2, 'running')
        RETURNING id
        """,
        opening_id, user_id,
    )
    return row["id"]


async def update_run_node(
    conn: asyncpg.Connection, run_id: int, node_name: str,
) -> None:
    """Update the current_node field for a run."""
    await conn.execute(
        "UPDATE job_opening_email_agent_runs SET current_node=$1 WHERE id=$2",
        node_name, run_id,
    )


async def complete_run(
    conn: asyncpg.Connection,
    run_id: int,
    status: str,
    state_json: str,
    events_json: str,
    error: str | None = None,
) -> None:
    """Finalize a run with its final status, state, events, and optional error."""
    await conn.execute(
        """
        UPDATE job_opening_email_agent_runs
        SET status=$1, state=$2::jsonb, events=$3::jsonb,
            completed_at=NOW(), error_message=$4, current_node=NULL
        WHERE id=$5
        """,
        status, state_json, events_json, error, run_id,
    )


async def get_run_output(
    conn: asyncpg.Connection, run_id: int,
) -> dict[str, Any]:
    """Return the output fields from a completed run's state."""
    row = await conn.fetchrow(
        """
        SELECT state, status, error_message
        FROM job_opening_email_agent_runs
        WHERE id=$1
        """,
        run_id,
    )
    if not row:
        return {}

    state = row["state"]
    if isinstance(state, str):
        state = json.loads(state)
    elif not isinstance(state, dict):
        return {}

    return {
        "generated_emails": state.get("generated_emails", []),
        "subject_lines": state.get("subject_lines", []),
        "followup_drafts": state.get("followup_drafts", []),
        "outreach_status": state.get("outreach_status"),
    }
