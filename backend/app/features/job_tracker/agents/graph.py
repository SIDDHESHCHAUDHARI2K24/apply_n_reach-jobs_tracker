"""LangGraph state graph definition for the resume-tailoring agent."""
from __future__ import annotations

from langgraph.graph import StateGraph, END

from app.features.job_tracker.agents.state import AgentState
from app.features.job_tracker.agents.nodes.node1_extract import node_extract
from app.features.job_tracker.agents.nodes.node2_select_template import node_select_template
from app.features.job_tracker.agents.nodes.node3_snapshot import node_snapshot
from app.features.job_tracker.agents.nodes.node4_triage import node_triage
from app.features.job_tracker.agents.nodes.node5a_experience import node_experience
from app.features.job_tracker.agents.nodes.node5b_projects import node_projects
from app.features.job_tracker.agents.nodes.node5c_skills import node_skills
from app.features.job_tracker.agents.nodes.node5d_personal import node_personal
from app.features.job_tracker.agents.nodes.node6_skills_certs import node_skills_certs
from app.features.job_tracker.agents.nodes.node7_render import node_render
from app.features.job_tracker.agents.nodes.node8_optimiser import (
    node_optimiser,
    should_continue_optimising,
)


def _check_error(state: AgentState) -> str:
    """Conditional edge: abort if an error occurred."""
    if state.get("error"):
        return "end"
    return "continue"


def build_graph() -> StateGraph:
    """Build and compile the resume-tailoring agent graph.

    Graph topology:
        extract → select_template → snapshot → triage
        → [experience, projects, skills, personal] (fan-out)
        → skills_certs (join)
        → render → optimiser ↔ render (loop) → end
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("extract", node_extract)
    graph.add_node("select_template", node_select_template)
    graph.add_node("snapshot", node_snapshot)
    graph.add_node("triage", node_triage)
    graph.add_node("experience", node_experience)
    graph.add_node("projects", node_projects)
    graph.add_node("skills", node_skills)
    graph.add_node("personal", node_personal)
    graph.add_node("skills_certs", node_skills_certs)
    graph.add_node("render", node_render)
    graph.add_node("optimiser", node_optimiser)

    # Set entry point
    graph.set_entry_point("extract")

    # Linear chain: extract → select_template → snapshot → triage
    graph.add_conditional_edges("extract", _check_error, {
        "continue": "select_template",
        "end": END,
    })
    graph.add_conditional_edges("select_template", _check_error, {
        "continue": "snapshot",
        "end": END,
    })
    graph.add_conditional_edges("snapshot", _check_error, {
        "continue": "triage",
        "end": END,
    })

    # Fan-out from triage: run all 4 tailoring nodes sequentially
    # (LangGraph doesn't natively fan-out async nodes, so we chain them)
    graph.add_edge("triage", "experience")
    graph.add_edge("experience", "projects")
    graph.add_edge("projects", "skills")
    graph.add_edge("skills", "personal")

    # Join → skills_certs
    graph.add_edge("personal", "skills_certs")

    # skills_certs → render
    graph.add_edge("skills_certs", "render")

    # render → optimiser
    graph.add_edge("render", "optimiser")

    # Optimiser conditional: loop back to render or end
    graph.add_conditional_edges("optimiser", should_continue_optimising, {
        "render": "render",
        "end": END,
    })

    return graph.compile()
