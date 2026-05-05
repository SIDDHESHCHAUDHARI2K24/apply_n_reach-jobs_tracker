"""FastAPI router for the email outreach agent."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.features.auth.utils import get_current_user
from app.features.core.config import get_settings
from app.features.core.dependencies import DbDep
from app.features.job_tracker.email_agent.runner import run_email_agent_stream
from app.features.job_tracker.email_agent.schemas import (
    EmailAgentOutputResponse,
    EmailAgentResumeRequest,
    EmailAgentRunListItem,
    EmailAgentRunResponse,
    EmailAgentStartRequest,
    EmailAgentStatusResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["email-agent"])


async def _verify_opening_ownership(
    conn: asyncpg.Connection, opening_id: int, user_id: int,
) -> None:
    """Verify the opening exists and belongs to the user."""
    row = await conn.fetchrow(
        "SELECT id FROM job_openings WHERE id=$1 AND user_id=$2",
        opening_id, user_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job opening not found")


async def _check_already_running(
    conn: asyncpg.Connection, opening_id: int, user_id: int,
) -> asyncpg.Record | None:
    """Return the latest run if it is currently running."""
    return await conn.fetchrow(
        """
        SELECT id, status FROM job_opening_email_agent_runs
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC LIMIT 1
        """,
        opening_id, user_id,
    )


@router.post(
    "/job-openings/{opening_id}/email-agent/run",
    status_code=202,
    response_model=EmailAgentRunResponse,
)
async def start_email_agent_run(
    opening_id: int,
    body: EmailAgentStartRequest,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> EmailAgentRunResponse:
    """Start a new email agent run for an opening. Returns 202 Accepted.

    Returns 409 if an email agent run is already in progress.
    """
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    latest = await _check_already_running(conn, opening_id, current_user["id"])
    if latest and latest["status"] == "running":
        raise HTTPException(status_code=409, detail="Email agent already running for this opening")

    run_row = await conn.fetchrow(
        """
        INSERT INTO job_opening_email_agent_runs (opening_id, user_id, status)
        VALUES ($1, $2, 'running')
        RETURNING id
        """,
        opening_id, current_user["id"],
    )

    settings = get_settings()
    background_tasks.add_task(
        _run_email_agent_background,
        opening_id,
        current_user["id"],
        run_row["id"],
        settings.database_url,
        body.recipient_type,
        body.raw_jd,
        body.raw_resume,
    )

    return EmailAgentRunResponse(
        run_id=run_row["id"],
        opening_id=opening_id,
        status="running",
        message="Email agent run started",
    )


async def _run_email_agent_background(
    opening_id: int,
    user_id: int,
    run_id: int,
    db_url: str,
    recipient_type: str,
    raw_jd: str | None,
    raw_resume: str | None,
) -> None:
    """Background task that runs the email agent with its own DB connection."""
    conn = await asyncpg.connect(db_url)
    try:
        async for event in run_email_agent_stream(
            conn, user_id, opening_id, run_id,
            recipient_type=recipient_type,
            raw_jd_override=raw_jd,
            raw_resume_override=raw_resume,
        ):
            logger.info("Email agent event: %s", event)
    except Exception:
        logger.exception("Email agent background task failed for run %d", run_id)
        await conn.execute(
            """
            UPDATE job_opening_email_agent_runs
            SET status='failed', error_message='Background task crashed', completed_at=NOW()
            WHERE id=$1
            """,
            run_id,
        )
    finally:
        await conn.close()


@router.get(
    "/job-openings/{opening_id}/email-agent/stream",
)
async def stream_email_agent_events(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> StreamingResponse:
    """SSE endpoint for streaming email agent events.

    Polls the email_agent_runs table and yields new events as SSE messages.
    Includes a heartbeat every 5 seconds.
    """
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    async def event_stream() -> AsyncIterator[str]:
        last_event_count = 0
        poll_count = 0
        max_polls = 120

        while poll_count < max_polls:
            run = await conn.fetchrow(
                """
                SELECT id, status, current_node, events, error_message
                FROM job_opening_email_agent_runs
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

                if len(events) > last_event_count:
                    for evt in events[last_event_count:]:
                        yield f"data: {json.dumps(evt)}\n\n"
                    last_event_count = len(events)

                if run["status"] in ("succeeded", "failed", "cancelled"):
                    yield f"data: {json.dumps({'node': 'agent', 'status': run['status'], 'message': run['error_message'] or 'Complete'})}\n\n"
                    return

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
    "/job-openings/{opening_id}/email-agent/status",
    response_model=EmailAgentStatusResponse,
)
async def get_email_agent_status(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> EmailAgentStatusResponse:
    """Get the current email agent status for an opening."""
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    run = await conn.fetchrow(
        """
        SELECT id, status, current_node, events, error_message, started_at, completed_at
        FROM job_opening_email_agent_runs
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC LIMIT 1
        """,
        opening_id, current_user["id"],
    )

    events = []
    agent_status = "idle"
    if run:
        events_raw = run["events"]
        if isinstance(events_raw, str):
            events = json.loads(events_raw)
        elif isinstance(events_raw, list):
            events = events_raw
        agent_status = run["status"]

    return EmailAgentStatusResponse(
        run_id=run["id"] if run else None,
        opening_id=opening_id,
        agent_status=agent_status,
        current_node=run["current_node"] if run else None,
        events=events,
        error_message=run["error_message"] if run else None,
        started_at=run["started_at"] if run else None,
        completed_at=run["completed_at"] if run else None,
    )


@router.get(
    "/job-openings/{opening_id}/email-agent/runs",
    response_model=list[EmailAgentRunListItem],
)
async def list_email_agent_runs(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> list[EmailAgentRunListItem]:
    """List all email agent runs for an opening, newest first."""
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    rows = await conn.fetch(
        """
        SELECT id, opening_id, status, current_node, error_message,
               started_at, completed_at, created_at
        FROM job_opening_email_agent_runs
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC
        """,
        opening_id, current_user["id"],
    )
    return [EmailAgentRunListItem(**dict(r)) for r in rows]


@router.post(
    "/job-openings/{opening_id}/email-agent/resume",
    status_code=202,
)
async def resume_email_agent(
    opening_id: int,
    body: EmailAgentResumeRequest,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> dict:
    """Resume a paused email agent run after human-in-the-loop edits.

    Accepts user_edits in the request body, updates the run state,
    and resumes graph execution.
    """
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    latest = await conn.fetchrow(
        """
        SELECT id, status, state
        FROM job_opening_email_agent_runs
        WHERE opening_id=$1 AND user_id=$2
        ORDER BY created_at DESC LIMIT 1
        """,
        opening_id, current_user["id"],
    )
    if not latest:
        raise HTTPException(status_code=404, detail="No email agent run found")
    if latest["status"] != "paused":
        raise HTTPException(status_code=400, detail=f"Cannot resume a run with status '{latest['status']}'")

    # Update state with user edits
    current_state = latest["state"]
    if isinstance(current_state, str):
        current_state = json.loads(current_state)
    elif not isinstance(current_state, dict):
        current_state = {}

    current_state["user_edits"] = body.user_edits

    await conn.execute(
        """
        UPDATE job_opening_email_agent_runs
        SET state=$1::jsonb, status='running'
        WHERE id=$2
        """,
        json.dumps(current_state), latest["id"],
    )

    settings = get_settings()
    background_tasks.add_task(
        _run_email_agent_background,
        opening_id,
        current_user["id"],
        latest["id"],
        settings.database_url,
        current_state.get("recipient_type", "recruiter"),
        None,  # raw_jd — use what's already in state
        None,  # raw_resume — use what's already in state
    )

    return {"run_id": latest["id"], "status": "running", "message": "Resumed"}


@router.get(
    "/job-openings/{opening_id}/email-agent/output",
    response_model=EmailAgentOutputResponse,
)
async def get_email_agent_output(
    opening_id: int,
    conn: asyncpg.Connection = DbDep,
    current_user: asyncpg.Record = Depends(get_current_user),
) -> EmailAgentOutputResponse:
    """Get the final output from the latest succeeded email agent run."""
    await _verify_opening_ownership(conn, opening_id, current_user["id"])

    run = await conn.fetchrow(
        """
        SELECT state, status
        FROM job_opening_email_agent_runs
        WHERE opening_id=$1 AND user_id=$2 AND status IN ('paused', 'succeeded')
        ORDER BY created_at DESC LIMIT 1
        """,
        opening_id, current_user["id"],
    )

    if not run:
        raise HTTPException(status_code=404, detail="No completed or paused email agent run found for this opening")

    state = run["state"]
    if isinstance(state, str):
        state = json.loads(state)
    elif not isinstance(state, dict):
        state = {}

    return EmailAgentOutputResponse(
        generated_emails=state.get("generated_emails", []),
        subject_lines=state.get("subject_lines", []),
        followup_drafts=state.get("followup_drafts", []),
        outreach_status=state.get("outreach_status"),
    )
