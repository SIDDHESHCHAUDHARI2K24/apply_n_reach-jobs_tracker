"""
nodes/export_node.py
---------------------
Node: export_node

Reads:  state["generated_emails"]
        state["user_edits"]         (populated by human-in-the-loop review)
        state["subject_lines"]
        state["followup_drafts"]
        state["verified_email"]
        state["outreach_status"]
Writes: state["outreach_status"]   → "drafted" (or updated from user_edits)
        state["generated_emails"]  → updated with user edits if present
        state["debug_log"]

Final node in the graph. Applies any user edits from the review step
back onto the generated email, then sets outreach_status to "drafted".

The UI status tracker takes over from here — it updates
outreach_status as the user copies, sends, and tracks replies.
"""

from __future__ import annotations

from app.features.job_tracker.email_agent.state import EmailAgentState, GeneratedEmail


async def export_node(state: EmailAgentState) -> dict:
    """
    LangGraph node — applies user edits and finalizes the outreach package.
    Sets outreach_status to 'drafted' to signal the graph is complete.
    """
    debug_log: list[str] = []
    debug_log.append("export_node: finalizing outreach package")

    generated_emails: list[GeneratedEmail] = list(state.get("generated_emails") or [])
    user_edits_list = state.get("user_edits") or []

    if user_edits_list and generated_emails:
        for edit in user_edits_list:
            for i, email in enumerate(generated_emails):
                if email["recipient_type"] == edit["recipient_type"]:
                    if edit.get("reset_to_ai"):
                        debug_log.append(
                            f"export_node: user reset '{edit['recipient_type']}' "
                            f"email to AI version"
                        )
                    else:
                        generated_emails[i] = {
                            **email,
                            "body": edit.get("edited_body", email["body"]),
                            "word_count": len(
                                edit.get("edited_body", email["body"]).split()
                            ),
                        }
                        debug_log.append(
                            f"export_node: applied user edits to "
                            f"'{edit['recipient_type']}' email"
                        )
                    break

    debug_log.append(
        f"export_node: package ready — "
        f"emails={len(generated_emails)} "
        f"subject_sets={len(state.get('subject_lines') or [])} "
        f"followups={len(state.get('followup_drafts') or [])} "
        f"verified_email={'yes' if state.get('verified_email') else 'no'}"
    )

    return {
        "generated_emails": generated_emails,
        "outreach_status": "drafted",
        "debug_log": state.get("debug_log", []) + debug_log,
    }
