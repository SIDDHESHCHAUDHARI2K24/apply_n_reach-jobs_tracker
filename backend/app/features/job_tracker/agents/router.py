"""FastAPI router for the resume-tailoring agent."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.features.auth.utils import get_current_user
from app.features.core.config import get_settings
from app.features.core.dependencies import DbDep
from app.features.job_tracker.agents.runner import run_agent_stream
from app.features.job_tracker.agents.schemas import (
    AgentRunListItem,
    AgentRunResponse,
    AgentStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["resume-agent"])


async def _verify_opening_ownership(
    conn: asyncpg.Connection, opening_id: int, user_id: int,
) -> asyncpg.Record:
    """Verify the opening exists and belongs to the user."""
    row = await conn.fetchrow(
        "SELECT id, agent_status, agent_run_id FROM job_openings WHERE id=$1 AND user_id=$2",
        opening_id, user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job opening not found")
    return row


@router.post(
    "/job-openings/{opening_id}/agent/run",
    status_code=202,
    response_model=AgentRunResponse,
)
async def start_agent_run(
    opening_id: int,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> AgentRunResponse:
    """Start a new agent run for an opening. Returns 202 Accepted.

    Returns 409 if an agent run is already in progress.
    """
    opening = await _verify_opening_ownership(conn, opening_id, current_user["id"])

    if opening["agent_status"] == "running":
        raise HTTPException(status_code=409, detail="Agent already running for this opening")

    # Create agent run record and mark opening as running atomically
    run = await conn.fetchrow(
        """
        INSERT INTO job_opening_agent_runs (opening_id, user_id, status)
        VALUES ($1, $2, 'running')
        RETURNING id
        """,
        opening_id, current_user["id"],
    )
    await conn.execute(
        "UPDATE job_openings SET agent_status='running', agent_run_id=$1 WHERE id=$2",
        run["id"], opening_id,
    )

    # Launch background task
    settings = get_settings()
    background_tasks.add_task(
        _run_agent_background, opening_id, current_user["id"], run["id"], settings.database_url,
    )

    return AgentRunResponse(
        run_id=run["id"],
        opening_id=opening_id,
        status="running",
        message="Agent run started",
    )


async def _run_agent_background(
    opening_id: int, user_id: int, run_id: int, db_url: str,
) -> None:
    """Background task that runs the agent with its own DB connection."""
    conn = await asyncpg.connect(db_url)
    try:
        async for event in run_agent_stream(conn, user_id, opening_id, run_id):
            logger.info("Agent event: %s", event)
    except Exception as exc:
        logger.exception("Agent background task failed for run %d", run_id)
        message = (str(exc).strip() or repr(exc))[:8000]
        if not message:
            message = type(exc).__name__
        error_message = f"{type(exc).__name__}: {message}"
        await conn.execute(
            """
            UPDATE job_opening_agent_runs
            SET status='failed', error_message=$2, completed_at=NOW()
            WHERE id=$1
            """,
            run_id,
            error_message,
        )
        await conn.execute(
            "UPDATE job_openings SET agent_status='failed' WHERE id=$1",
            opening_id,
        )
    finally:
        await conn.close()


@router.get(
    "/job-openings/{opening_id}/agent/stream",
)
async def stream_agent_events(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> StreamingResponse:
    """SSE endpoint for streaming agent events.

    Polls the agent_runs table and yields new events as SSE messages.
    Includes a heartbeat every 5 seconds.
    """
    opening = await _verify_opening_ownership(conn, opening_id, current_user["id"])

    async def event_stream() -> AsyncIterator[str]:
        last_event_count = 0
        poll_count = 0
        max_polls = 120  # 10 minutes at 5s intervals

        while poll_count < max_polls:
            run = await conn.fetchrow(
                """
                SELECT id, status, current_node, events, error_message
                FROM job_opening_agent_runs
                WHERE opening_id=$1 AND user_id=$2
                ORDER BY created_at DESC LIMIT 1
                """,
                opening_id, current_user["id"],
            )

            if run:
                events_raw = run["events"]
                if isinstance(events_raw, str):
                    events = json.loads(events_raw)
                elif isinstance(events_raw, list):
                    events = events_raw
                else:
                    events = []

                # Yield any new events
                if len(events) > last_event_count:
                    for evt in events[last_event_count:]:
                        yield f"data: {json.dumps(evt)}\n\n"
                    last_event_count = len(events)

                # Check if done
                if run["status"] in ("succeeded", "failed", "cancelled"):
                    yield f"data: {json.dumps({'node': 'agent', 'status': run['status'], 'message': run['error_message'] or 'Complete'})}\n\n"
                    return

            # Heartbeat
            yield f": heartbeat\n\n"
            await asyncio.sleep(5)
            poll_count += 1

        yield f"data: {json.dumps({'node': 'agent', 'status': 'timeout', 'message': 'Stream timed out'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/job-openings/{opening_id}/agent/status",
    response_model=AgentStatusResponse,
)
async def get_agent_status(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> AgentStatusResponse:
    """Get the current agent status for an opening."""
    opening = await _verify_opening_ownership(conn, opening_id, current_user["id"])

    run = await conn.fetchrow(
        """
        SELECT id, status, current_node, events, error_message, started_at, completed_at
        FROM job_opening_agent_runs
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC LIMIT 1
        """,
        opening_id, current_user["id"],
    )

    events = []
    if run:
        events_raw = run["events"]
        if isinstance(events_raw, str):
            events = json.loads(events_raw)
        elif isinstance(events_raw, list):
            events = events_raw

    return AgentStatusResponse(
        run_id=run["id"] if run else None,
        opening_id=opening_id,
        agent_status=opening["agent_status"],
        current_node=run["current_node"] if run else None,
        events=events,
        error_message=run["error_message"] if run else None,
        started_at=run["started_at"] if run else None,
        completed_at=run["completed_at"] if run else None,
    )


@router.get(
    "/job-openings/{opening_id}/agent/runs",
    response_model=list[AgentRunListItem],
)
async def list_agent_runs(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[AgentRunListItem]:
    """List all agent runs for an opening, newest first."""
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    rows = await conn.fetch(
        """
        SELECT id, opening_id, status, current_node, error_message,
               started_at, completed_at, created_at
        FROM job_opening_agent_runs
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC
        """,
        opening_id, current_user["id"],
    )
    return [AgentRunListItem(**dict(r)) for r in rows]
