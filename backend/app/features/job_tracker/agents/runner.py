"""Agent runner — executes the LangGraph agent and yields events."""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator

import asyncpg

from app.features.job_tracker.agents.config import configure_langsmith
from app.features.job_tracker.agents.graph import build_graph
from app.features.job_tracker.agents.mcp_server import AgentContext, set_context
from app.features.job_tracker.agents.state import AgentEvent, AgentState

logger = logging.getLogger(__name__)


async def run_agent_stream(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    run_id: int,
) -> AsyncIterator[AgentEvent]:
    """Execute the resume agent and yield events as they occur.

    Sets up the MCP context, runs the compiled graph, persists state
    to the agent_runs table, and yields events for SSE streaming.
    """
    configure_langsmith()

    # Set up tool context
    ctx = AgentContext(user_id=user_id, conn=conn, opening_id=opening_id)
    set_context(ctx)

    # Mark run as running
    await conn.execute(
        "UPDATE job_opening_agent_runs SET status='running', current_node='extract' WHERE id=$1",
        run_id,
    )
    await conn.execute(
        "UPDATE job_openings SET agent_status='running', agent_run_id=$1 WHERE id=$2",
        run_id, opening_id,
    )

    yield AgentEvent(node="agent", status="started", message="Agent started")

    try:
        graph = build_graph()
        initial_state: AgentState = {
            "opening_id": opening_id,
            "user_id": user_id,
            "run_id": run_id,
            "events": [],
            "render_count": 0,
            "optimiser_iterations": 0,
        }

        # Stream through graph nodes
        final_state = initial_state
        emitted_event_count = 0  # Track how many events we've already yielded
        async for event in graph.astream(initial_state):
            # LangGraph yields {node_name: state_update} dicts
            for node_name, state_update in event.items():
                if isinstance(state_update, dict):
                    # Merge state update into final_state
                    final_state = {**final_state, **state_update}

                    # Update current node in DB
                    await conn.execute(
                        "UPDATE job_opening_agent_runs SET current_node=$1 WHERE id=$2",
                        node_name, run_id,
                    )

                    # Yield only NEW events (delta from the cumulative list)
                    all_events = final_state.get("events", [])
                    new_events = all_events[emitted_event_count:]
                    for evt in new_events:
                        yield evt
                    emitted_event_count = len(all_events)

                    # Check for errors
                    if state_update.get("error"):
                        logger.warning(
                            "Agent error at node %s: %s",
                            node_name, state_update["error"],
                        )

        # Determine final status
        error = final_state.get("error")
        final_status = "failed" if error else "succeeded"

        # Persist final state
        await conn.execute(
            """
            UPDATE job_opening_agent_runs
            SET status=$1, state=$2::jsonb, events=$3::jsonb,
                completed_at=NOW(), error_message=$4, current_node=NULL
            WHERE id=$5
            """,
            final_status,
            json.dumps(_sanitize_state(final_state)),
            json.dumps(final_state.get("events", [])),
            error,
            run_id,
        )
        await conn.execute(
            "UPDATE job_openings SET agent_status=$1 WHERE id=$2",
            final_status, opening_id,
        )

        yield AgentEvent(
            node="agent",
            status=final_status,
            message=error or "Agent completed successfully",
        )

    except Exception as e:
        logger.exception("Agent runner crashed")
        # Mark as failed
        await conn.execute(
            """
            UPDATE job_opening_agent_runs
            SET status='failed', error_message=$1, completed_at=NOW()
            WHERE id=$2
            """,
            str(e), run_id,
        )
        await conn.execute(
            "UPDATE job_openings SET agent_status='failed' WHERE id=$1",
            opening_id,
        )
        yield AgentEvent(node="agent", status="error", message=str(e))


def _sanitize_state(state: dict[str, Any]) -> dict[str, Any]:
    """Remove non-serializable values from state for JSON storage."""
    safe = {}
    for k, v in state.items():
        if k == "events":
            continue  # Stored separately
        try:
            json.dumps(v)
            safe[k] = v
        except (TypeError, ValueError):
            safe[k] = str(v)
    return safe
