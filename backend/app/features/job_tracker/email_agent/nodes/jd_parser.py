"""
nodes/jd_parser.py
------------------
Node: jd_parser

Reads:  state["raw_jd"]
Writes: state["parsed_jd"]
        state["errors"]     (appended on partial parse)
        state["debug_log"]  (appended always)

Parses the raw job description text into a structured ParsedJD object
using a prompted LLM call. Handles varied JD formats (bullet lists,
prose, hybrid). Missing optional fields are set to None rather than
raising — the node never blocks the graph for a missing team name.
"""

from __future__ import annotations

import json

from app.features.job_tracker.email_agent.state import EmailAgentState, ParsedJD
from app.features.job_tracker.email_agent.nodes import _chat

_SYSTEM = """
You are a job description parser. Extract structured information from the
job description provided by the user and return ONLY a valid JSON object —
no preamble, no markdown, no explanation.

Return this exact shape:
{
  "role_title": "string",
  "company_name": "string",
  "team_name": "string or null",
  "location": "string or null",
  "required_skills": ["string", ...],
  "responsibilities": ["string", ...],
  "tone_signals": ["string", ...]
}

Rules:
- required_skills: hard technical skills only (e.g. "Python", "Kubernetes", "SQL").
  Max 10 items. Omit soft skills.
- responsibilities: key bullet points summarizing what the role does.
  Max 8 items, each under 15 words.
- tone_signals: adjectives or short phrases describing the team/company culture
  as implied by the JD (e.g. "fast-paced", "data-driven", "collaborative").
  Max 5 items. Empty list if none are implied.
- If a field cannot be determined from the text, use null for strings
  or an empty list for arrays.
""".strip()


async def jd_parser(state: EmailAgentState) -> dict:
    """
    LangGraph node — parses the raw job description into a structured object.

    Returns a partial state dict containing only the fields this node updates.
    LangGraph merges these into the running state automatically.
    """
    raw_jd = state["raw_jd"]
    errors: list[str] = []
    debug_log: list[str] = []

    debug_log.append("jd_parser: starting parse")

    try:
        raw_json = await _chat(system=_SYSTEM, user=raw_jd, max_tokens=1024)
        data = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        errors.append(f"jd_parser: LLM returned invalid JSON — {exc}")
        debug_log.append("jd_parser: falling back to empty ParsedJD")
        return {
            "parsed_jd": _empty_parsed_jd(raw_jd),
            "errors": state.get("errors", []) + errors,
            "debug_log": state.get("debug_log", []) + debug_log,
        }
    except Exception as exc:
        errors.append(f"jd_parser: API call failed — {exc}")
        return {
            "parsed_jd": _empty_parsed_jd(raw_jd),
            "errors": state.get("errors", []) + errors,
            "debug_log": state.get("debug_log", []) + debug_log,
        }

    # Warn on missing optional fields but do not block
    if not data.get("team_name"):
        errors.append("jd_parser: team_name not found in JD — using None")
    if not data.get("location"):
        errors.append("jd_parser: location not found in JD — using None")

    parsed_jd: ParsedJD = {
        "role_title":       data.get("role_title", "Unknown Role"),
        "company_name":     data.get("company_name", "Unknown Company"),
        "team_name":        data.get("team_name"),
        "location":         data.get("location"),
        "required_skills":  data.get("required_skills", []),
        "responsibilities": data.get("responsibilities", []),
        "tone_signals":     data.get("tone_signals", []),
        "raw_text":         raw_jd,
    }

    debug_log.append(
        f"jd_parser: parsed role='{parsed_jd['role_title']}' "
        f"company='{parsed_jd['company_name']}' "
        f"skills={len(parsed_jd['required_skills'])} "
        f"responsibilities={len(parsed_jd['responsibilities'])}"
    )

    return {
        "parsed_jd": parsed_jd,
        "errors": state.get("errors", []) + errors,
        "debug_log": state.get("debug_log", []) + debug_log,
    }


def _empty_parsed_jd(raw_jd: str) -> ParsedJD:
    """Fallback ParsedJD used when parsing fails — keeps graph running."""
    return ParsedJD(
        role_title="Unknown Role",
        company_name="Unknown Company",
        team_name=None,
        location=None,
        required_skills=[],
        responsibilities=[],
        tone_signals=[],
        raw_text=raw_jd,
    )
