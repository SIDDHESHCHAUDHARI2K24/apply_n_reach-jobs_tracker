"""LangGraph graph definition for the email outreach agent."""
from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from app.features.job_tracker.email_agent.state import EmailAgentState
from app.features.job_tracker.email_agent.nodes import (
    jd_parser,
    resume_extractor,
    contact_lookup,
    linkedin_input,
    email_generator,
    subject_generator,
    export_node,
)


def _check_error(state: EmailAgentState) -> str:
    """Conditional edge: abort if an error occurred."""
    if state.get("error"):
        return "end"
    return "continue"


def _checked_route_after_contact_lookup(state: EmailAgentState) -> str:
    """Conditional edge from contact_lookup: error check + Apollo result routing."""
    if state.get("error"):
        return "end"
    if state.get("verified_email"):
        return "email_generator"
    return "linkedin_input"


def build_graph() -> StateGraph:
    """Build and compile the email outreach agent graph.

    Graph topology:
        START → jd_parser → resume_extractor → contact_lookup
                                    ├── verified email → email_generator
                                    ├── found, no email → linkedin_input → email_generator
                                    └── not found → linkedin_input → email_generator
                                    → subject_generator → export_node (HITL interrupt) → END
    """
    graph = StateGraph(EmailAgentState)

    graph.add_node("jd_parser", jd_parser)
    graph.add_node("resume_extractor", resume_extractor)
    graph.add_node("contact_lookup", contact_lookup)
    graph.add_node("linkedin_input", linkedin_input)
    graph.add_node("email_generator", email_generator)
    graph.add_node("subject_generator", subject_generator)
    graph.add_node("export_node", export_node)

    graph.add_edge(START, "jd_parser")

    graph.add_conditional_edges("jd_parser", _check_error, {
        "continue": "resume_extractor",
        "end": END,
    })

    graph.add_conditional_edges("resume_extractor", _check_error, {
        "continue": "contact_lookup",
        "end": END,
    })

    graph.add_conditional_edges("contact_lookup", _checked_route_after_contact_lookup, {
        "end": END,
        "email_generator": "email_generator",
        "linkedin_input": "linkedin_input",
    })

    graph.add_edge("linkedin_input", "email_generator")

    graph.add_conditional_edges("email_generator", _check_error, {
        "continue": "subject_generator",
        "end": END,
    })

    graph.add_conditional_edges("subject_generator", _check_error, {
        "continue": "export_node",
        "end": END,
    })

    graph.add_edge("export_node", END)

    return graph.compile(interrupt_before=["export_node"])
