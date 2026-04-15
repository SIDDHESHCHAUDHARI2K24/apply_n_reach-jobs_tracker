"""LaTeX template builder for Jake's Resume-style documents.

Builds a complete compilable LaTeX string from aggregated job profile data.
Uses string concatenation (NOT pylatex Document objects) because pylatex's
Document API is incompatible with Jake's custom macro approach.
"""
from __future__ import annotations

import re

from app.features.job_profile.latex_resume.schemas import ResumeLayoutOptions


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def latex_escape(text: str | None) -> str:
    """Escape special LaTeX characters in user-supplied text.

    Returns an empty string for None or empty input.  Characters are
    replaced in a specific order so earlier replacements are not
    double-processed by later ones (backslash must come first).
    """
    if not text:
        return ""

    # Order matters — backslash first so we don't double-escape later replacements.
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for char, replacement in replacements:
        text = text.replace(char, replacement)
    return text


def sanitize_url_for_href(url: str | None) -> str:
    """Return a URL safe for use inside a LaTeX \\href{} command.

    - Returns ``""`` for None or empty input.
    - Accepts URLs that start with http:// or https:// (case-insensitive).
    - Replaces bare ``%`` characters (not already part of a percent-encoded
      sequence like ``%20``) with ``\\%``.
    - Returns ``""`` for anything that does not look like a valid URL.
    """
    if not url or not url.strip():
        return ""

    url = url.strip()

    if not re.match(r"^https?://", url, re.IGNORECASE):
        return ""

    # Escape any bare % signs that are NOT already part of a valid percent-
    # encoded sequence (two hex digits following the %).
    safe_url = re.sub(r"%(?![0-9A-Fa-f]{2})", r"\\%", url)
    return safe_url


# ---------------------------------------------------------------------------
# Preamble builder
# ---------------------------------------------------------------------------

def _build_preamble(layout: ResumeLayoutOptions) -> str:
    """Return the full LaTeX preamble (documentclass → custom commands)."""

    body_pt = layout.body_font_size_pt

    # Geometry margin specification
    if layout.margins_in is None:
        margin_spec = "margin=0.5in"
    else:
        m = layout.margins_in
        margin_spec = f"top={m.top}in, bottom={m.bottom}in, left={m.left}in, right={m.right}in"

    preamble = rf"""\documentclass[letterpaper,{body_pt}pt]{{article}}

\usepackage[empty]{{fullpage}}
\usepackage{{titlesec}}
\usepackage[usenames,dvipsnames]{{color}}
\usepackage{{enumitem}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{fancyhdr}}
\usepackage[english]{{babel}}
\usepackage{{tabularx}}
\usepackage[{margin_spec}]{{geometry}}
\input glyphtounicode

\pagestyle{{fancy}}
\fancyhf{{}}
\fancyfoot{{}}
\renewcommand{{\headrulewidth}}{{0pt}}
\renewcommand{{\footrulewidth}}{{0pt}}

\addtolength{{\oddsidemargin}}{{-0.5in}}
\addtolength{{\evensidemargin}}{{-0.5in}}
\addtolength{{\textwidth}}{{1in}}
\addtolength{{\topmargin}}{{-.5in}}
\addtolength{{\textheight}}{{1.0in}}

\urlstyle{{same}}

\raggedbottom
\raggedright
\setlength{{\tabcolsep}}{{0in}}

\titleformat{{\section}}{{
  \vspace{{-4pt}}\scshape\raggedright\large
}}{{}}{{0em}}{{}}[\color{{black}}\titlerule \vspace{{-5pt}}]

\pdfgentounicode=1

% Custom commands
\newcommand{{\resumeItem}}[1]{{
  \item\small{{
    {{#1 \vspace{{-2pt}}}}
  }}
}}

\newcommand{{\resumeSubheading}}[4]{{
  \vspace{{-2pt}}\item
    \begin{{tabular*}}{{0.97\textwidth}}[t]{{l@{{\extracolsep{{\fill}}}}r}}
      \textbf{{#1}} & #2 \\
      \textit{{\small#3}} & \textit{{\small #4}} \\
    \end{{tabular*}}\vspace{{-7pt}}
}}

\newcommand{{\resumeSubSubheading}}[2]{{
    \item
    \begin{{tabular*}}{{0.97\textwidth}}{{l@{{\extracolsep{{\fill}}}}r}}
      \textit{{\small#1}} & \textit{{\small #2}} \\
    \end{{tabular*}}\vspace{{-7pt}}
}}

\newcommand{{\resumeProjectHeading}}[2]{{
    \item
    \begin{{tabular*}}{{0.97\textwidth}}{{l@{{\extracolsep{{\fill}}}}r}}
      \small#1 & #2 \\
    \end{{tabular*}}\vspace{{-7pt}}
}}

\newcommand{{\resumeSubItem}}[1]{{\resumeItem{{#1}}}}

\renewcommand\labelitemii{{$\vcenter{{\hbox{{\tiny$\bullet$}}}}$}}

\newcommand{{\resumeSubHeadingListStart}}{{\begin{{itemize}}[leftmargin=0.15in, label={{}}]}}
\newcommand{{\resumeSubHeadingListEnd}}{{\end{{itemize}}}}
\newcommand{{\resumeItemListStart}}{{\begin{{itemize}}}}
\newcommand{{\resumeItemListEnd}}{{\end{{itemize}}\vspace{{-5pt}}}}
"""
    return preamble


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def _build_header(personal: dict, job_meta: dict, layout: ResumeLayoutOptions) -> str:
    """Build the resume header (name + contact line + optional target role)."""
    name_pt = layout.name_font_size_pt
    name_pt_plus2 = name_pt + 2

    name_escaped = latex_escape(personal.get("full_name") or "")
    email_escaped = latex_escape(personal.get("email") or "")

    contact_parts: list[str] = []
    if email_escaped:
        contact_parts.append(email_escaped)

    linkedin_raw = personal.get("linkedin_url")
    if linkedin_raw:
        href = sanitize_url_for_href(linkedin_raw)
        if href:
            # Extract a display handle if possible (linkedin.com/in/handle)
            match = re.search(r"linkedin\.com/in/([^/?#]+)", linkedin_raw, re.IGNORECASE)
            display = f"linkedin.com/in/{match.group(1)}" if match else "LinkedIn"
            contact_parts.append(rf"\href{{{href}}}{{{latex_escape(display)}}}")

    github_raw = personal.get("github_url")
    if github_raw:
        href = sanitize_url_for_href(github_raw)
        if href:
            match = re.search(r"github\.com/([^/?#]+)", github_raw, re.IGNORECASE)
            display = f"github.com/{match.group(1)}" if match else "GitHub"
            contact_parts.append(rf"\href{{{href}}}{{{latex_escape(display)}}}")

    portfolio_raw = personal.get("portfolio_url")
    if portfolio_raw:
        href = sanitize_url_for_href(portfolio_raw)
        if href:
            contact_parts.append(rf"\href{{{href}}}{{portfolio}}")

    contact_line = r" $|$ ".join(contact_parts)

    lines: list[str] = [
        r"\begin{center}",
        rf"    \textbf{{\fontsize{{{name_pt}}}{{{name_pt_plus2}}}\selectfont {name_escaped}}} \\ \vspace{{1pt}}",
        rf"    \small {contact_line}",
        r"\end{center}",
    ]

    target_role = (job_meta or {}).get("target_role")
    if target_role:
        lines.insert(-1, rf"    \small{{\textit{{{latex_escape(target_role)}}}}}")

    return "\n".join(lines) + "\n"


def _build_education(educations: list[dict]) -> str:
    """Build the Education section.  Returns empty string if list is empty."""
    if not educations:
        return ""

    parts: list[str] = [
        r"\section{Education}",
        r"\resumeSubHeadingListStart",
    ]

    for edu in educations:
        university = latex_escape(edu.get("university_name") or "")
        major = latex_escape(edu.get("major") or "")
        degree_type = latex_escape(edu.get("degree_type") or "")
        start = edu.get("start_month_year") or ""
        end = edu.get("end_month_year") or "Present"
        date_range = f"{latex_escape(start)} -- {latex_escape(end)}" if start else latex_escape(end)

        degree_major = f"{degree_type}, {major}" if degree_type and major else degree_type or major

        parts.append(
            rf"  \resumeSubheading{{{university}}}{{{date_range}}}{{{degree_major}}}{{}}"
        )

        bullets = [b for b in (edu.get("bullet_points") or []) if b and b.strip()]
        if bullets:
            parts.append(r"  \resumeItemListStart")
            for bullet in bullets:
                parts.append(rf"    \resumeItem{{{latex_escape(bullet)}}}")
            parts.append(r"  \resumeItemListEnd")

    parts.append(r"\resumeSubHeadingListEnd")
    parts.append("")
    return "\n".join(parts) + "\n"


def _build_experience(experiences: list[dict]) -> str:
    """Build the Experience section.  Returns empty string if list is empty."""
    if not experiences:
        return ""

    parts: list[str] = [
        r"\section{Experience}",
        r"\resumeSubHeadingListStart",
    ]

    for exp in experiences:
        company = latex_escape(exp.get("company_name") or "")
        role = latex_escape(exp.get("role_title") or "")
        start = exp.get("start_month_year") or ""
        end = exp.get("end_month_year") or "Present"
        date_range = f"{latex_escape(start)} -- {latex_escape(end)}" if start else latex_escape(end)
        context = exp.get("context") or ""

        parts.append(
            rf"  \resumeSubheading{{{company}}}{{{date_range}}}{{{role}}}{{}}"
        )

        # Optional context intro line
        if context and context.strip():
            parts.append(rf"  \small{{{latex_escape(context)}}}")

        bullets = [b for b in (exp.get("bullet_points") or []) if b and b.strip()]
        work_links = [u for u in (exp.get("work_sample_links") or []) if u and u.strip()]

        if bullets or work_links:
            parts.append(r"  \resumeItemListStart")
            for bullet in bullets:
                parts.append(rf"    \resumeItem{{{latex_escape(bullet)}}}")
            if work_links:
                link_strs = []
                for url in work_links:
                    href = sanitize_url_for_href(url)
                    if href:
                        link_strs.append(rf"\href{{{href}}}{{{latex_escape(url)}}}")
                if link_strs:
                    parts.append(rf"    \resumeItem{{{', '.join(link_strs)}}}")
            parts.append(r"  \resumeItemListEnd")

    parts.append(r"\resumeSubHeadingListEnd")
    parts.append("")
    return "\n".join(parts) + "\n"


def _build_projects(projects: list[dict]) -> str:
    """Build the Projects section.  Returns empty string if list is empty."""
    if not projects:
        return ""

    parts: list[str] = [
        r"\section{Projects}",
        r"\resumeSubHeadingListStart",
    ]

    for proj in projects:
        name = latex_escape(proj.get("project_name") or "")
        start = proj.get("start_month_year") or ""
        end = proj.get("end_month_year") or ""
        if start and end:
            date_range = f"{latex_escape(start)} -- {latex_escape(end)}"
        elif start:
            date_range = latex_escape(start)
        else:
            date_range = ""

        parts.append(rf"  \resumeProjectHeading{{\textbf{{{name}}}}}{{{date_range}}}")

        description = proj.get("description") or ""
        ref_links = [u for u in (proj.get("reference_links") or []) if u and u.strip()]

        if description and description.strip() or ref_links:
            parts.append(r"  \resumeItemListStart")
            if description and description.strip():
                parts.append(rf"    \resumeItem{{{latex_escape(description)}}}")
            if ref_links:
                link_strs = []
                for url in ref_links:
                    href = sanitize_url_for_href(url)
                    if href:
                        link_strs.append(rf"\href{{{href}}}{{{latex_escape(url)}}}")
                if link_strs:
                    parts.append(rf"    \resumeItem{{{', '.join(link_strs)}}}")
            parts.append(r"  \resumeItemListEnd")

    parts.append(r"\resumeSubHeadingListEnd")
    parts.append("")
    return "\n".join(parts) + "\n"


def _build_research(researches: list[dict]) -> str:
    """Build the Research section.  Returns empty string if list is empty."""
    if not researches:
        return ""

    parts: list[str] = [
        r"\section{Research}",
        r"\resumeSubHeadingListStart",
    ]

    for res in researches:
        paper_name = latex_escape(res.get("paper_name") or "")
        pub_link_raw = res.get("publication_link") or ""
        description = res.get("description") or ""

        parts.append(rf"  \resumeProjectHeading{{\textbf{{{paper_name}}}}}{{}}")

        bullets: list[str] = []
        if pub_link_raw and pub_link_raw.strip():
            href = sanitize_url_for_href(pub_link_raw)
            if href:
                bullets.append(rf"\href{{{href}}}{{View Publication}}")
        if description and description.strip():
            bullets.append(latex_escape(description))

        if bullets:
            parts.append(r"  \resumeItemListStart")
            for b in bullets:
                parts.append(rf"    \resumeItem{{{b}}}")
            parts.append(r"  \resumeItemListEnd")

    parts.append(r"\resumeSubHeadingListEnd")
    parts.append("")
    return "\n".join(parts) + "\n"


def _build_certifications(certifications: list[dict]) -> str:
    """Build the Certifications section.  Returns empty string if list is empty."""
    if not certifications:
        return ""

    parts: list[str] = [
        r"\section{Certifications}",
        r"\resumeSubHeadingListStart",
    ]

    for cert in certifications:
        cert_name = latex_escape(cert.get("certification_name") or "")
        verify_raw = cert.get("verification_link") or ""
        href = sanitize_url_for_href(verify_raw)

        if href:
            item_text = rf"{cert_name} -- \href{{{href}}}{{Verify}}"
        else:
            item_text = cert_name

        parts.append(rf"  \resumeSubItem{{{item_text}}}")

    parts.append(r"\resumeSubHeadingListEnd")
    parts.append("")
    return "\n".join(parts) + "\n"


def _build_skills(skill_items: list[dict]) -> str:
    """Build the Technical Skills section.  Returns empty string if list is empty."""
    if not skill_items:
        return ""

    technical: list[dict] = []
    competency: list[dict] = []

    for item in skill_items:
        kind = (item.get("kind") or "").lower()
        if kind == "technical":
            technical.append(item)
        elif kind == "competency":
            competency.append(item)

    technical.sort(key=lambda x: x.get("sort_order") or 0)
    competency.sort(key=lambda x: x.get("sort_order") or 0)

    if not technical and not competency:
        return ""

    rows: list[str] = []
    if technical:
        names = ", ".join(latex_escape(s.get("name") or "") for s in technical)
        rows.append(rf"     \textbf{{Technical Skills}}{{: {names}}} \\")
    if competency:
        names = ", ".join(latex_escape(s.get("name") or "") for s in competency)
        rows.append(rf"     \textbf{{Competencies}}{{: {names}}}")

    inner = "\n".join(rows)
    section = (
        r"\section{Technical Skills}" + "\n"
        r"\begin{itemize}[leftmargin=0.15in, label={}]" + "\n"
        r"    \small{\item{" + "\n"
        + inner + "\n"
        r"    }}" + "\n"
        r"\end{itemize}" + "\n"
    )
    return section + "\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_latex_document(profile_data: dict, layout: ResumeLayoutOptions) -> str:
    """Build a complete Jake's Resume-style LaTeX document string.

    Parameters
    ----------
    profile_data:
        Dict with keys: personal, job_meta, educations, experiences,
        projects, researches, certifications, skill_items.
    layout:
        Font sizes and margin settings.

    Returns
    -------
    str
        A compilable LaTeX document string.
    """
    personal = profile_data.get("personal") or {}
    job_meta = profile_data.get("job_meta") or {}
    educations = profile_data.get("educations") or []
    experiences = profile_data.get("experiences") or []
    projects = profile_data.get("projects") or []
    researches = profile_data.get("researches") or []
    certifications = profile_data.get("certifications") or []
    skill_items = profile_data.get("skill_items") or []

    preamble = _build_preamble(layout)
    header = _build_header(personal, job_meta, layout)
    education = _build_education(educations)
    experience = _build_experience(experiences)
    projects_section = _build_projects(projects)
    research_section = _build_research(researches)
    certifications_section = _build_certifications(certifications)
    skills_section = _build_skills(skill_items)

    body_parts = [
        r"\begin{document}",
        "",
        header,
        education,
        experience,
        projects_section,
        research_section,
        certifications_section,
        skills_section,
        r"\end{document}",
    ]

    document = preamble + "\n".join(body_parts) + "\n"
    return document
