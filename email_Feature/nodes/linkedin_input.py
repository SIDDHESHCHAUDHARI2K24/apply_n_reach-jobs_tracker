"""
nodes/linkedin_input.py
------------------------
Node: linkedin_input

Reads:  state["raw_linkedin_paste"]   (set by UI before this node runs)
Writes: state["linkedin_context"]
        state["errors"]
        state["debug_log"]

NOTE: raw_linkedin_paste is not in the base OutreachState schema because
it is only populated when the user provides LinkedIn context (optional step
in the wizard). The graph only routes here when:
  (a) the user explicitly provided a LinkedIn paste in the UI (T4.1 step 3), OR
  (b) Apollo found a person but no verified email (T2.4 fallback branch).

In case (b), the UI should prompt the user to paste the LinkedIn profile
before the graph resumes from the interrupt checkpoint.

Parses free-form pasted LinkedIn content (About section, post text,
manual description) into a structured LinkedInContext object using Claude.
No LinkedIn API dependency — works reliably for the prototype.
"""

from __future__ import annotations

import json

from llm import chat
from state import OutreachState, LinkedInContext

_SYSTEM = """
You are a LinkedIn profile parser. Extract structured information from the
pasted LinkedIn content provided by the user.

Return ONLY a valid JSON object — no preamble, no markdown, no explanation.

Return this exact shape:
{
  "full_name": "string or null",
  "current_role": "string or null",
  "current_company": "string or null",
  "recent_posts": ["string", ...],
  "notable_projects": ["string", ...],
  "shared_connections": ["string", ...]
}

Rules:
- full_name: person's full name if clearly stated, else null.
- current_role: their current job title, else null.
- current_company: their current employer, else null.
- recent_posts: up to 3 topics or titles of posts/articles they shared,
  described in 10 words or fewer each. Empty list if none found.
- notable_projects: up to 3 projects, products, or initiatives they worked on
  that are mentioned in the profile, described in 10 words or fewer each.
  Empty list if none found.
- shared_connections: any mutual connections the user mentioned in their paste.
  Empty list if none.
- If content is too sparse to extract anything useful, return nulls and
  empty lists rather than guessing.
""".strip()


def linkedin_input(state: OutreachState) -> dict:
    """
    LangGraph node — parses user-pasted LinkedIn content into a structured
    LinkedInContext object for use in email personalization.
    """
    errors: list[str] = []
    debug_log: list[str] = []

    debug_log.append("linkedin_input: starting LinkedIn context parse")

    # raw_linkedin_paste is an ad-hoc field set by the UI/caller.
    # We read it safely with .get() so the node doesn't crash if absent.
    raw_paste: str | None = state.get("raw_linkedin_paste")  # type: ignore[typeddict-item]

    if not raw_paste or not raw_paste.strip():
        errors.append(
            "linkedin_input: no LinkedIn paste provided — "
            "linkedin_context will be None, personalization signals unavailable"
        )
        debug_log.append("linkedin_input: skipping — empty paste")
        return {
            "linkedin_context": None,
            "errors": errors,
            "debug_log": debug_log,
        }

    try:
        raw_json = chat(system=_SYSTEM, user=raw_paste, max_tokens=512)
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"linkedin_input: LLM returned invalid JSON — {exc}")
        return {
            "linkedin_context": None,
            "errors": errors,
            "debug_log": debug_log,
        }
    except Exception as exc:
        errors.append(f"linkedin_input: API call failed — {exc}")
        return {
            "linkedin_context": None,
            "errors": errors,
            "debug_log": debug_log,
        }

    linkedin_context: LinkedInContext = {
        "full_name":          data.get("full_name"),
        "current_role":       data.get("current_role"),
        "current_company":    data.get("current_company"),
        "recent_posts":       data.get("recent_posts", []),
        "notable_projects":   data.get("notable_projects", []),
        "shared_connections": data.get("shared_connections", []),
        "raw_paste":          raw_paste,
    }

    # Update contact_name from LinkedIn if Apollo didn't find one
    updates: dict = {
        "linkedin_context": linkedin_context,
        "errors": errors,
        "debug_log": debug_log,
    }

    if state.get("contact_name") is None and linkedin_context.get("full_name"):
        updates["contact_name"] = linkedin_context["full_name"]
        debug_log.append(
            f"linkedin_input: contact_name set from LinkedIn: "
            f"'{linkedin_context['full_name']}'"
        )

    if state.get("contact_title") is None and linkedin_context.get("current_role"):
        updates["contact_title"] = linkedin_context["current_role"]

    signals = (
        len(linkedin_context["recent_posts"])
        + len(linkedin_context["notable_projects"])
        + len(linkedin_context["shared_connections"])
    )
    debug_log.append(
        f"linkedin_input: parsed context — "
        f"name='{linkedin_context.get('full_name')}' "
        f"personalization_signals={signals}"
    )

    return updates
