"""
graph.py
---------
LangGraph workflow for the AI-Powered Outreach Email feature.

Graph structure (linear → conditional → HITL → export):

  [START]
     │
     ▼
  jd_parser          Parses raw JD into structured ParsedJD
     │
     ▼
  resume_extractor   Selects relevant skills/achievements vs JD
     │
     ▼
  contact_lookup     Queries Apollo.io for verified contact email
     │
     ▼ (conditional router — see route_after_contact_lookup)
     ├── apollo verified email found ──────────────────────────┐
     │                                                          │
     ├── apollo person found, no verified email ──► linkedin_input ─┤
     │                                                          │
     └── apollo no person found ──────────────────► linkedin_input ─┘
                                                               │
                                                               ▼
                                                        email_generator
                                                               │
                                                               ▼
                                                       subject_generator
                                                               │
                                                      interrupt (HITL) ◄── UI review (T4.3)
                                                               │
                                                               ▼
                                                          export_node
                                                               │
                                                            [END]

Conditional branching logic (T5.3):
  - apollo_result.found = True AND verified_email is not None
      → skip linkedin_input, go directly to email_generator
  - apollo_result.found = True AND verified_email is None
      → route to linkedin_input (person found, no email — use LinkedIn for context)
  - apollo_result.found = False
      → route to linkedin_input (no person found — LinkedIn as fallback)

Human-in-the-loop (T5.4):
  The graph uses LangGraph's interrupt_before mechanism on export_node.
  When the graph reaches export_node, it pauses and returns control to the
  caller. The UI then presents the generated emails for review and edit (T4.3).
  The caller resumes the graph by invoking it again with the same thread_id
  and the user's edits written into state["user_edits"].

Usage:
    from graph import build_graph
    from state import initial_state

    graph = build_graph()

    # First invocation — runs until HITL interrupt
    config = {"configurable": {"thread_id": "user-123-job-456"}}
    state = initial_state(raw_jd=..., raw_resume=..., recipient_type="recruiter")
    result = graph.invoke(state, config=config)
    # result is the state snapshot at the interrupt point
    # → send result["generated_emails"] and result["subject_lines"] to the UI

    # Second invocation — resume after user edits
    graph.invoke(
        {"user_edits": [{"recipient_type": "recruiter", "edited_body": "...", ...}]},
        config=config,
    )
    # → graph runs export_node and reaches END
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env")

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from state import OutreachState
from nodes.jd_parser import jd_parser
from nodes.resume_extractor import resume_extractor
from nodes.contact_lookup import contact_lookup
from nodes.linkedin_input import linkedin_input
from nodes.email_generator import email_generator
from nodes.subject_generator import subject_generator
from nodes.export_node import export_node


# ---------------------------------------------------------------------------
# Conditional router (T5.3)
# ---------------------------------------------------------------------------

def route_after_contact_lookup(state: OutreachState) -> str:
    """
    Inspects the apollo_result to decide which node runs next.

    Returns the name of the next node — LangGraph uses this string to
    resolve the destination via add_conditional_edges.

    Decision table:
      verified_email present                → "email_generator"  (skip LinkedIn)
      found=True but no verified email      → "linkedin_input"   (enrich from LinkedIn)
      found=False (no person at all)        → "linkedin_input"   (LinkedIn as fallback)
    """
    apollo_result = state.get("apollo_result")

    # Happy path — Apollo found a verified email, no enrichment needed
    if state.get("verified_email"):
        return "email_generator"

    # Person found but no verified email, OR no person found at all —
    # both route to linkedin_input for enrichment / fallback draft.
    return "linkedin_input"


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    """
    Constructs, compiles, and returns the outreach email LangGraph graph.

    The graph uses MemorySaver as its checkpointer to enable:
      1. State persistence across the HITL interrupt.
      2. Graph resumption on the second invoke() call.

    In production, replace MemorySaver with a persistent backend
    (e.g. langgraph.checkpoint.postgres.PostgresSaver) so state
    survives server restarts.

    Returns:
        A compiled LangGraph graph ready to invoke().
    """
    builder = StateGraph(OutreachState)

    # --- Register nodes ---
    builder.add_node("jd_parser",          jd_parser)
    builder.add_node("resume_extractor",   resume_extractor)
    builder.add_node("contact_lookup",     contact_lookup)
    builder.add_node("linkedin_input",     linkedin_input)
    builder.add_node("email_generator",    email_generator)
    builder.add_node("subject_generator",  subject_generator)
    builder.add_node("export_node",        export_node)

    # --- Linear edges (no branching) ---
    builder.add_edge(START,              "jd_parser")
    builder.add_edge("jd_parser",        "resume_extractor")
    builder.add_edge("resume_extractor", "contact_lookup")

    # --- Conditional edge after Apollo lookup (T5.3) ---
    builder.add_conditional_edges(
        "contact_lookup",
        route_after_contact_lookup,
        {
            "email_generator": "email_generator",
            "linkedin_input":  "linkedin_input",
        },
    )

    # linkedin_input always flows into email_generator
    builder.add_edge("linkedin_input",    "email_generator")
    builder.add_edge("email_generator",   "subject_generator")
    builder.add_edge("subject_generator", "export_node")
    builder.add_edge("export_node",       END)

    # --- Compile with HITL interrupt before export_node (T5.4) ---
    checkpointer = MemorySaver()
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["export_node"],   # pause here for UI review
    )

    return graph


# ---------------------------------------------------------------------------
# Convenience: pre-built singleton for import
# ---------------------------------------------------------------------------

# Import and use this directly in your API layer:
#   from graph import graph
#   result = graph.invoke(state, config=config)
graph = build_graph()
