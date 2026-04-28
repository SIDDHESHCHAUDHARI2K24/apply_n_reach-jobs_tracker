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
import re
from urllib.parse import urlparse

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

_RECRUITER_PRIORITY_TERMS = [
    "recruiter",
    "talent acquisition",
    "technical recruiter",
    "senior recruiter",
    "principal recruiter",
    "staffing",
    "sourcer",
    "talent partner",
]

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
    manual_contact_name: str | None = state.get("manual_contact_name")  # type: ignore[typeddict-item]

    if parsed_jd is None:
        errors.append("contact_lookup: parsed_jd is None — cannot determine company")
        return _not_found_result(
            source="apollo",
            errors=errors,
            debug_log=debug_log,
            reason="parsed_jd missing",
            manual_contact_name=manual_contact_name,
        )

    api_key = os.environ.get("APOLLO_API_KEY")
    if not api_key:
        errors.append("contact_lookup: APOLLO_API_KEY not set — skipping Apollo lookup")
        return _not_found_result(
            source="apollo",
            errors=errors,
            debug_log=debug_log,
            reason="no API key",
            manual_contact_name=manual_contact_name,
        )

    company_name = parsed_jd["company_name"]
    title_filters = _TITLE_FILTERS.get(recipient_type, [])
    org_scope = _resolve_apollo_org_scope(api_key=api_key, company_name=company_name)

    debug_log.append(
        f"contact_lookup: searching company='{company_name}' "
        f"recipient_type='{recipient_type}' "
        f"title_filters={title_filters[:2]}..."
    )

    # Apollo query strategy:
    # 1) strict email + titles
    # 2) relaxed email + titles
    # 3) relaxed email + no title filters
    try:
        people, strategy = _search_people_with_fallbacks(
            api_key=api_key,
            company_name=company_name,
            title_filters=title_filters,
            org_scope=org_scope,
        )
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

    if strategy:
        debug_log.append(f"contact_lookup: people found using strategy='{strategy}'")

    if not people:
        errors.append(
            f"contact_lookup: Apollo returned no results for "
            f"company='{company_name}' recipient_type='{recipient_type}'"
        )
        return _not_found_result("apollo", errors, debug_log, "no results")

    # Guard against loose Apollo matches (wrong company with similar keywords).
    matched_people = [p for p in people if _company_matches_target(p, company_name)]
    if not matched_people:
        sample_name = _extract_name(people[0]) or "unknown contact"
        sample_company = _extract_person_company(people[0]) or "unknown company"
        errors.append(
            "contact_lookup: Apollo returned contacts, but none matched target "
            f"company='{company_name}' (top result='{sample_name}' at '{sample_company}')"
        )
        return _not_found_result("apollo", errors, debug_log, "company mismatch")

    people = _rank_people(people=matched_people, recipient_type=recipient_type)

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
        display_name = _extract_name(person) or "unknown contact"
        email_status = person.get("email_status") or "unknown"
        display_title = _extract_title(person) or "unknown title"
        errors.append(
            f"contact_lookup: Apollo found '{display_name}' "
            f"({display_title}) but no usable email (status='{email_status}') — routing to LinkedIn fallback"
        )
        apollo_result: ApolloResult = {
            "found": True,
            "person_id": person.get("id"),
            "full_name": _extract_name(person),
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
            "contact_name": manual_contact_name or _extract_name(person),
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
        full_name=_extract_name(chosen),
        title=_extract_title(chosen),
        company=company_name,
        email=chosen.get("email"),
        email_status=email_status,
        linkedin_url=chosen.get("linkedin_url"),
        source="apollo",
    )

    debug_log.append(
        f"contact_lookup: found contact='{_extract_name(chosen)}' "
        f"title='{_extract_title(chosen)}' "
        f"email_status='{email_status}'"
    )

    return {
        "apollo_result": apollo_result,
        "verified_email": chosen.get("email"),
        "contact_name": manual_contact_name or _extract_name(chosen),
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


def _extract_name(person: dict) -> str | None:
    """Extract a stable display name from an Apollo person record."""
    # Apollo often returns first/last even when `name` is None.
    first = (person.get("first_name") or "").strip()
    last = (person.get("last_name") or "").strip()
    first_last = f"{first} {last}".strip()
    full_name = person.get("name") or person.get("full_name") or first_last
    if not full_name:
        full_name = _name_from_linkedin_url(person.get("linkedin_url"))
    return full_name or None


def _normalize_company(text: str | None) -> str:
    """Normalize company strings to improve matching robustness."""
    if not text:
        return ""
    normalized = text.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\b(inc|incorporated|llc|ltd|corp|corporation|co|company)\b", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _extract_person_company(person: dict) -> str | None:
    """Extract the best available company name from an Apollo person object."""
    organization = person.get("organization") or {}
    employment_history = person.get("employment_history") or []

    return (
        organization.get("name")
        or person.get("organization_name")
        or person.get("account", {}).get("name")
        or (employment_history[0].get("organization_name") if employment_history else None)
    )


def _company_matches_target(person: dict, target_company: str) -> bool:
    """True when person company appears to match target company name."""
    person_company = _normalize_company(_extract_person_company(person))
    target = _normalize_company(target_company)
    if not person_company or not target:
        return False

    # Accept substring containment either way after normalization
    # (e.g., "caci international" vs "caci international inc").
    return person_company in target or target in person_company


def _rank_people(people: list[dict], recipient_type: str) -> list[dict]:
    """Rank Apollo people by recipient-type title relevance."""
    wanted_terms = [t.lower() for t in _TITLE_FILTERS.get(recipient_type, [])]
    if not wanted_terms:
        return people

    def score(person: dict) -> tuple[int, int, int, int]:
        title = (_extract_title(person) or "").lower()
        if not title:
            return (0, 0, 0, 0)
        wanted_score = sum(1 for term in wanted_terms if term in title)
        recruiter_bonus = 0
        recruiter_exact = 0
        if recipient_type == "recruiter":
            recruiter_bonus = sum(1 for term in _RECRUITER_PRIORITY_TERMS if term in title)
            # Prefer explicit recruiter titles over broader TA matches.
            if re.search(r"\brecruiter\b", title):
                recruiter_exact = 2
            if "talent acquisition recruiter" in title:
                recruiter_exact -= 1
        has_full_name = int(bool(_extract_name(person)))
        return (wanted_score, recruiter_exact, recruiter_bonus, has_full_name)

    return sorted(people, key=score, reverse=True)


def _apollo_search(
    api_key: str,
    company_name: str,
    title_filters: list[str],
    contact_email_status: list[str] | None,
    per_page: int = 3,
    org_scope: dict | None = None,
    page: int = 1,
) -> dict:
    """Call Apollo mixed_people/api_search with optional email-status filter."""
    payload = {"per_page": per_page, "page": page}
    if title_filters:
        payload["person_titles"] = title_filters

    # IMPORTANT: Apollo mixed_people/api_search can return empty or noisy
    # results when multiple org-scoping params are combined. Use one strategy.
    org_id = (org_scope or {}).get("org_id")
    org_domain = (org_scope or {}).get("org_domain")
    if org_id:
        payload["organization_ids"] = [org_id]
    elif org_domain:
        payload["organization_domains"] = [org_domain]
    else:
        payload["organization_names"] = [company_name]
    if contact_email_status:
        payload["contact_email_status"] = contact_email_status

    response = requests.post(
        f"{_BASE_URL}/mixed_people/api_search",
        headers={
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
            "X-Api-Key": api_key,
        },
        json=payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _name_from_linkedin_url(linkedin_url: str | None) -> str | None:
    """Derive a readable full name from a LinkedIn profile URL slug."""
    if not linkedin_url:
        return None
    try:
        path = urlparse(linkedin_url).path.strip("/")
    except Exception:
        return None
    if not path:
        return None
    parts = [p for p in path.split("/") if p]
    if not parts:
        return None
    slug = parts[-1]
    slug = re.sub(r"\d+$", "", slug)  # trim trailing numeric suffixes
    tokens = [t for t in re.split(r"[-_]+", slug) if t and t.lower() not in {"in", "pub"}]
    if len(tokens) < 2:
        return None
    return " ".join(token.capitalize() for token in tokens[:3])


def _search_people_with_fallbacks(
    api_key: str,
    company_name: str,
    title_filters: list[str],
    org_scope: dict | None,
) -> tuple[list[dict], str | None]:
    """Run progressive Apollo search strategies, return first non-empty result."""
    attempts = [
        ("strict_email_with_titles", ["verified", "likely_valid"], title_filters, 5),
        ("any_email_with_titles", None, title_filters, 8),
        ("any_email_no_titles", None, [], 10),
    ]

    for label, email_filter, titles, per_page in attempts:
        people = _apollo_search_pages(
            api_key=api_key,
            company_name=company_name,
            title_filters=titles,
            contact_email_status=email_filter,
            per_page=per_page,
            max_pages=5,
            org_scope=org_scope,
        )
        if people:
            return people, label

    return [], None


def _apollo_search_pages(
    api_key: str,
    company_name: str,
    title_filters: list[str],
    contact_email_status: list[str] | None,
    per_page: int,
    max_pages: int,
    org_scope: dict | None,
) -> list[dict]:
    """Collect people across multiple pages, deduplicated by Apollo id."""
    seen_ids: set[str] = set()
    collected: list[dict] = []

    for page in range(1, max_pages + 1):
        data = _apollo_search(
            api_key=api_key,
            company_name=company_name,
            title_filters=title_filters,
            contact_email_status=contact_email_status,
            per_page=per_page,
            org_scope=org_scope,
            page=page,
        )
        people = data.get("people", [])
        if not people:
            break

        added = 0
        for person in people:
            pid = person.get("id")
            key = str(pid) if pid else f"{_extract_name(person)}::{_extract_title(person)}"
            if key in seen_ids:
                continue
            seen_ids.add(key)
            collected.append(person)
            added += 1

        # Stop when page does not add anything new.
        if added == 0:
            break

    return collected


def _resolve_apollo_org_scope(api_key: str, company_name: str) -> dict:
    """
    Resolve an Apollo organization id/domain from a company name.

    Returns a dict with optional keys:
      - org_id
      - org_domain
    Falls back to {} when lookup fails.
    """
    orgs: list[dict] = []
    for name_candidate in _company_name_candidates(company_name):
        payload = {"q_organization_name": name_candidate, "page": 1, "per_page": 5}
        try:
            response = requests.post(
                f"{_BASE_URL}/organizations/search",
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                    "X-Api-Key": api_key,
                },
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            continue

        orgs = data.get("organizations") or []
        if orgs:
            break

    if not orgs:
        return {}

    target = _normalize_company(company_name)
    best = None
    for org in orgs:
        candidate = _normalize_company(org.get("name"))
        if not candidate:
            continue
        if candidate == target:
            best = org
            break
        if best is None and (candidate in target or target in candidate):
            best = org

    if best is None:
        best = orgs[0]

    return {
        "org_id": best.get("id"),
        "org_domain": best.get("primary_domain") or best.get("domain"),
    }


def _company_name_candidates(company_name: str) -> list[str]:
    """Generate candidate company names for organization lookup."""
    normalized = company_name.strip()
    base = re.sub(
        r"\b(inc|inc\.|incorporated|llc|ltd|corp|corp\.|corporation|co|company)\b",
        "",
        normalized,
        flags=re.IGNORECASE,
    )
    base = re.sub(r"\s+", " ", base).strip()
    candidates = [normalized]
    if base and base.lower() != normalized.lower():
        candidates.append(base)
    if " international " in f" {base.lower()} ":
        candidates.append(re.sub(r"\binternational\b", "", base, flags=re.IGNORECASE).strip())
    # Preserve order while removing empties/duplicates.
    seen: set[str] = set()
    result: list[str] = []
    for cand in candidates:
        key = cand.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(cand.strip())
    return result


def _not_found_result(
    source: str,
    errors: list[str],
    debug_log: list[str],
    reason: str,
    manual_contact_name: str | None = None,
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
        "contact_name": manual_contact_name,
        "contact_title": None,
        "errors": errors,
        "debug_log": debug_log,
    }
