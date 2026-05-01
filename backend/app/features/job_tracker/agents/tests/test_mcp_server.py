"""Tests for the MCP server tool module."""
import pytest
from app.features.job_tracker.agents.mcp_server import (
    get_agent_tools,
    get_context,
    set_context,
    AgentContext,
)


def test_get_agent_tools_returns_tools():
    """get_agent_tools should return a list of StructuredTools."""
    tools = get_agent_tools()
    assert len(tools) > 0
    names = {t.name for t in tools}
    assert "list_education" in names
    assert "list_experience" in names
    assert "create_education" in names
    assert "update_personal" in names
    assert "render_resume_pdf" in names
    assert "count_pdf_pages" in names
    assert "update_agent_state" in names
    assert "create_opening_resume" in names
    assert "get_extracted_details" in names


def test_get_context_raises_without_init():
    """get_context should raise RuntimeError if not initialized."""
    set_context(None)
    with pytest.raises(RuntimeError, match="Agent context not initialized"):
        get_context()


def test_tool_count():
    """Should have the expected number of tools."""
    tools = get_agent_tools()
    # 7 sections * ~3-4 ops + snapshot + extraction + render + pdf + pages + state
    assert len(tools) >= 25
