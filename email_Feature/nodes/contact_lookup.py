"""
nodes/contact_lookup.py
------------------------
Node: contact_lookup

Reads:  state["parsed_jd"]        (company name, role context)
        state["recipient_type"]    (drives Apollo title filters)
Writes: state["apollo_result"]
        state["verified_email"]    (None if not found/verified)
        state["contact_name"]      (None if not found)
        state["contact_title"]     (None if not found)
        state["errors"]
        state["debug_log"]

Queries the Apollo.io People Search API to find the most relevant contact
at the target company based on recipient type. Applies a verification filter
— only "verified" or "likely_valid" emails are promoted to verified_email.

The apollo_result field is always populated after this node runs (even on
failure) so the conditional router in graph.py can make a branching decision.
If Apollo is unavailable or returns no usable result, the graph branches to
the LinkedIn fallback or manual input path.

Apollo API docs: https://apolloio.github.io/apollo-api-docs/
Environment variable required: APOLLO_API_KEY
"""

from __future__ import annotations

import os
import time

import requests

from state import OutreachState, ApolloResult

_BASE_URL = "https://api.apollo.io/v1"

# Title keyword filters per recipient type.
# Apollo's people/search accepts a `person_titles` array — we pass the
# most specific terms first so ranking favors the tightest match.
_TITLE_FILTERS: dict[str, list[str]] = {
    "recruiter": [
        "recruiter",
        "talent acquisition",
        "technical recruiter",
        "sourcer",
        "talent partner",
    ],
    "hiring_manager": [
        "engineering manager",
        "director of engineering",
        "vp of engineering",
        "head of engineering",
        "product manager",
        "director of product",
    ],
    "team_member": [
        "software engineer",
        "machine learning engineer",
        "data scientist",
        "data engineer",
        "senior engineer",
        "staff engineer",
    ],
}

# Email statuses Apollo considers usable. We treat "likely_valid" as
# acceptable for prototype purposes but flag it in debug_log.
_ACCEPTABLE_STATUSES = {"verified", "likely_valid"}


def contact_lookup(state: OutreachState) -> dict:
    """
    LangGraph node — queries Apollo.io to find a verified contact at the
    target company based on recipient_type.
    """
    errors: list[str] = []
    debug_log: list[str] = []

    debug_log.append("contact_lookup: starting Apollo search")

    parsed_jd = state.get("parsed_jd")
    recipient_type = state["recipient_type"]

    if parsed_jd is None:
        errors.append("contact_lookup: parsed_jd is None — cannot determine company")
        return _not_found_result(
            source="apollo",
            errors=errors,
            debug_log=debug_log,
            reason="parsed_jd missing",
        )

    api_key = os.environ.get("APOLLO_API_KEY")
    if not api_key:
        errors.append("contact_lookup: APOLLO_API_KEY not set — skipping Apollo lookup")
        return _not_found_result(
            source="apollo",
            errors=errors,
            debug_log=debug_log,
            reason="no API key",
        )

    company_name = parsed_jd["company_name"]
    title_filters = _TITLE_FILTERS.get(recipient_type, [])

    debug_log.append(
        f"contact_lookup: searching company='{company_name}' "
        f"recipient_type='{recipient_type}' "
        f"title_filters={title_filters[:2]}..."
    )

    # --- Apollo People Search ---
    try:
        response = requests.post(
            f"{_BASE_URL}/mixed_people/api_search",
            headers={
                "Content-Type": "application/json",
                "Cache-Control": "no-cache",
                "X-Api-Key": api_key,
            },
            json={
                "organization_names": [company_name],
                "person_titles": title_filters,
                "contact_email_status": ["verified", "likely_valid"],
                "per_page": 3,      # fetch top 3, pick the best
                "page": 1,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        errors.append("contact_lookup: Apollo API timed out")
        return _not_found_result("apollo", errors, debug_log, "timeout")
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 429:
            errors.append("contact_lookup: Apollo API rate limit hit — retry later")
        else:
            errors.append(f"contact_lookup: Apollo API error {exc.response.status_code}")
        return _not_found_result("apollo", errors, debug_log, str(exc))
    except Exception as exc:
        errors.append(f"contact_lookup: unexpected error — {exc}")
        return _not_found_result("apollo", errors, debug_log, str(exc))

    people = data.get("people", [])
    if not people:
        errors.append(
            f"contact_lookup: Apollo returned no results for "
            f"company='{company_name}' recipient_type='{recipient_type}'"
        )
        return _not_found_result("apollo", errors, debug_log, "no results")

    # Pick the first person who has a usable email — Apollo already
    # filtered by email status in the query but we verify here defensively.
    chosen = None
    for person in people:
        email_status = (person.get("email_status") or "").lower().replace(" ", "_")
        if email_status in _ACCEPTABLE_STATUSES and person.get("email"):
            chosen = person
            break

    if chosen is None:
        # People found but none had a usable email — common when Apollo has
        # a contact record without email data.
        person = people[0]
        errors.append(
            f"contact_lookup: Apollo found person '{person.get('name')}' "
            f"but no verified email — routing to LinkedIn fallback"
        )
        apollo_result: ApolloResult = {
            "found": True,
            "person_id": person.get("id"),
            "full_name": person.get("name") or person.get("full_name") or person.get("first_name", "") + " " + person.get("last_name", ""),
            "title": _extract_title(person),
            "company": company_name,
            "email": None,
            "email_status": person.get("email_status"),
            "linkedin_url": person.get("linkedin_url"),
            "source": "apollo",
        }
        return {
            "apollo_result": apollo_result,
            "verified_email": None,
            "contact_name": person.get("name") or person.get("full_name") or (person.get("first_name", "") + " " + person.get("last_name", "")).strip(),
            "contact_title": _extract_title(person),
            "errors": errors,
            "debug_log": debug_log,
        }

    # Happy path — verified contact with email found.
    email_status = (chosen.get("email_status") or "").lower().replace(" ", "_")
    if email_status == "likely_valid":
        debug_log.append(
            f"contact_lookup: email status is 'likely_valid' (not 'verified') "
            f"for {chosen.get('email')} — proceeding but flagged"
        )

    apollo_result = ApolloResult(
        found=True,
        person_id=chosen.get("id"),
        full_name=chosen.get("name") or chosen.get("full_name") or (chosen.get("first_name", "") + " " + chosen.get("last_name", "")).strip(),
        title=_extract_title(chosen),
        company=company_name,
        email=chosen.get("email"),
        email_status=email_status,
        linkedin_url=chosen.get("linkedin_url"),
        source="apollo",
    )

    debug_log.append(
        f"contact_lookup: found contact='{chosen.get('name')}' "
        f"title='{_extract_title(chosen)}' "
        f"email_status='{email_status}'"
    )

    return {
        "apollo_result": apollo_result,
        "verified_email": chosen.get("email"),
        "contact_name": chosen.get("name"),
        "contact_title": _extract_title(chosen),
        "errors": errors,
        "debug_log": debug_log,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_title(person: dict) -> str | None:
    """Extract the most useful title string from an Apollo person record."""
    return (
        person.get("title")
        or person.get("headline")
        or None
    )


def _not_found_result(
    source: str,
    errors: list[str],
    debug_log: list[str],
    reason: str,
) -> dict:
    """
    Return a consistent 'not found' partial state update.
    apollo_result.found = False signals the conditional router to take
    the fallback branch (LinkedIn or manual input).
    """
    debug_log.append(f"contact_lookup: returning not-found result — reason: {reason}")
    apollo_result: ApolloResult = {
        "found": False,
        "person_id": None,
        "full_name": None,
        "title": None,
        "company": None,
        "email": None,
        "email_status": None,
        "linkedin_url": None,
        "source": source,
    }
    return {
        "apollo_result": apollo_result,
        "verified_email": None,
        "contact_name": None,
        "contact_title": None,
        "errors": errors,
        "debug_log": debug_log,
    }
