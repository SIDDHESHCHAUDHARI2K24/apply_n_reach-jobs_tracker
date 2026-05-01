"""Database model helpers for email agent.

Tables managed by Alembic (see alembic/versions/).
This module provides helper functions for querying email agent data.
"""
from __future__ import annotations

import asyncpg

# Table name constants for reference
EMAIL_AGENT_RUNS_TABLE = "job_opening_email_agent_runs"

# Status enum values
EMAIL_AGENT_STATUS_VALUES = ("idle", "running", "paused", "succeeded", "failed")


async def get_latest_email_agent_run(
    conn: asyncpg.Connection, opening_id: int, user_id: int,
) -> asyncpg.Record | None:
    return await conn.fetchrow(
        f"""
        SELECT id, opening_id, user_id, status, current_node,
               state, events, error_message, started_at, completed_at, created_at
        FROM {EMAIL_AGENT_RUNS_TABLE}
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC LIMIT 1
        """,
        opening_id, user_id,
    )
