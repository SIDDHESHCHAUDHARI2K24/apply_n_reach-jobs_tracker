"""Service layer for the latex_resume sub-feature.

Orchestrates: aggregate job profile data → build LaTeX → render PDF → upsert row.
"""
import json
import re

import asyncpg
from fastapi import HTTPException, status

from app.features.job_profile.latex_resume import models
from app.features.job_profile.latex_resume.renderer import LatexCompileError, render_pdf
from app.features.job_profile.latex_resume.schemas import ResumeLayoutOptions
from app.features.job_profile.latex_resume.template_builder import build_latex_document


async def aggregate_job_profile_data(
    conn: asyncpg.Connection, job_profile_id: int
) -> dict:
    """Fetch all section data for a job profile and return as a structured dict."""
    # Job profile meta
    jp_row = await conn.fetchrow(
        "SELECT profile_name, target_role, target_company, job_posting_url "
        "FROM job_profiles WHERE id = $1",
        job_profile_id,
    )
    job_meta = dict(jp_row) if jp_row else {}

    # Personal details (1:1)
    personal_row = await conn.fetchrow(
        "SELECT full_name, email, linkedin_url, github_url, portfolio_url "
        "FROM job_profile_personal_details WHERE job_profile_id = $1",
        job_profile_id,
    )
    personal = dict(personal_row) if personal_row else {}

    # Education
    edu_rows = await conn.fetch(
        "SELECT university_name, major, degree_type, start_month_year, end_month_year, "
        "bullet_points, reference_links "
        "FROM job_profile_educations WHERE job_profile_id = $1 ORDER BY start_month_year DESC",
        job_profile_id,
    )
    educations = [_row_to_dict(r) for r in edu_rows]

    # Experience
    exp_rows = await conn.fetch(
        "SELECT role_title, company_name, location, start_month_year, end_month_year, "
        "context, work_sample_links, bullet_points "
        "FROM job_profile_experiences WHERE job_profile_id = $1 ORDER BY start_month_year DESC",
        job_profile_id,
    )
    experiences = [_row_to_dict(r) for r in exp_rows]

    # Projects
    proj_rows = await conn.fetch(
        "SELECT project_name, description, start_month_year, end_month_year, reference_links "
        "FROM job_profile_projects WHERE job_profile_id = $1 ORDER BY created_at DESC",
        job_profile_id,
    )
    projects = [_row_to_dict(r) for r in proj_rows]

    # Research
    res_rows = await conn.fetch(
        "SELECT paper_name, publication_link, description "
        "FROM job_profile_researches WHERE job_profile_id = $1 ORDER BY created_at DESC",
        job_profile_id,
    )
    researches = [_row_to_dict(r) for r in res_rows]

    # Certifications
    cert_rows = await conn.fetch(
        "SELECT certification_name, verification_link "
        "FROM job_profile_certifications WHERE job_profile_id = $1 ORDER BY created_at DESC",
        job_profile_id,
    )
    certifications = [_row_to_dict(r) for r in cert_rows]

    # Skills
    skill_rows = await conn.fetch(
        "SELECT kind, name, sort_order "
        "FROM job_profile_skill_items WHERE job_profile_id = $1 ORDER BY sort_order ASC",
        job_profile_id,
    )
    skill_items = [dict(r) for r in skill_rows]

    return {
        "personal": personal,
        "job_meta": job_meta,
        "educations": educations,
        "experiences": experiences,
        "projects": projects,
        "researches": researches,
        "certifications": certifications,
        "skill_items": skill_items,
    }


def _row_to_dict(row: asyncpg.Record) -> dict:
    """Convert an asyncpg Record to a dict, deserializing JSONB string fields."""
    d = dict(row)
    for key, val in d.items():
        if isinstance(val, str):
            # asyncpg returns JSONB from RETURNING as str; SELECT returns list/dict natively
            # Be defensive: try to parse if it looks like JSON
            stripped = val.strip()
            if stripped.startswith(("[", "{")):
                try:
                    d[key] = json.loads(val)
                except (json.JSONDecodeError, ValueError):
                    pass
    return d


def _build_filename_stem(profile_data: dict) -> str:
    """Build PDF filename stem: firstname_lastname_rolename or firstname_lastname_profilename."""
    personal = profile_data.get("personal") or {}
    job_meta = profile_data.get("job_meta") or {}

    full_name = personal.get("full_name") or ""
    name_parts = full_name.strip().split()
    if len(name_parts) >= 2:
        first = name_parts[0]
        last = name_parts[-1]
    elif name_parts:
        first = name_parts[0]
        last = ""
    else:
        first = "resume"
        last = ""

    role = job_meta.get("target_role") or job_meta.get("profile_name") or ""

    parts = [p for p in [first, last, role] if p]
    stem = "_".join(parts).replace(" ", "_").lower()

    # Keep only alphanumeric, underscore, hyphen
    stem = re.sub(r"[^\w\-]", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")

    return stem or "resume"


async def render_resume(
    conn: asyncpg.Connection,
    job_profile_id: int,
    layout: ResumeLayoutOptions | None,
) -> dict:
    """Full render pipeline: aggregate → build LaTeX → compile PDF → upsert.

    Returns the updated rendered_resume row as a dict.
    """
    if layout is None:
        layout = ResumeLayoutOptions()

    await models.ensure_rendered_resume_schema(conn)

    profile_data = await aggregate_job_profile_data(conn, job_profile_id)

    latex_source = build_latex_document(profile_data, layout)
    filename_stem = _build_filename_stem(profile_data)

    try:
        pdf_bytes = render_pdf(latex_source, filename_stem=filename_stem)
    except LatexCompileError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LaTeX compilation failed: {exc}. Log: {exc.log_tail[:500] if exc.log_tail else 'no log'}",
        )

    layout_json_str = json.dumps(layout.model_dump())

    row = await conn.fetchrow(
        """
        INSERT INTO rendered_resume
            (job_profile_id, latex_source, pdf_content, layout_json, template_name, rendered_at)
        VALUES ($1, $2, $3, $4::jsonb, $5, NOW())
        ON CONFLICT (job_profile_id) DO UPDATE SET
            latex_source = EXCLUDED.latex_source,
            pdf_content = EXCLUDED.pdf_content,
            layout_json = EXCLUDED.layout_json,
            template_name = EXCLUDED.template_name,
            rendered_at = NOW(),
            updated_at = NOW()
        RETURNING job_profile_id, template_name, rendered_at, layout_json
        """,
        job_profile_id,
        latex_source,
        pdf_bytes,
        layout_json_str,
        "jakes_resume_v1",
    )

    return _finalize_row(dict(row))


async def get_rendered_resume(
    conn: asyncpg.Connection, job_profile_id: int
) -> dict | None:
    """Fetch render metadata (no PDF bytes). Returns None if never rendered."""
    await models.ensure_rendered_resume_schema(conn)
    row = await conn.fetchrow(
        "SELECT job_profile_id, template_name, rendered_at, layout_json "
        "FROM rendered_resume WHERE job_profile_id = $1",
        job_profile_id,
    )
    if row is None:
        return None
    return _finalize_row(dict(row))


async def get_resume_pdf(
    conn: asyncpg.Connection, job_profile_id: int
) -> tuple[bytes, str] | None:
    """Fetch PDF bytes + filename stem. Returns None if never rendered."""
    await models.ensure_rendered_resume_schema(conn)
    # Also need personal + job_meta for filename
    row = await conn.fetchrow(
        "SELECT rr.pdf_content, jp.profile_name, jp.target_role, "
        "       jpd.full_name "
        "FROM rendered_resume rr "
        "JOIN job_profiles jp ON jp.id = rr.job_profile_id "
        "LEFT JOIN job_profile_personal_details jpd ON jpd.job_profile_id = rr.job_profile_id "
        "WHERE rr.job_profile_id = $1",
        job_profile_id,
    )
    if row is None:
        return None

    stem = _build_filename_stem({
        "personal": {"full_name": row["full_name"]},
        "job_meta": {"target_role": row["target_role"], "profile_name": row["profile_name"]},
    })
    return row["pdf_content"], stem


def _finalize_row(d: dict) -> dict:
    """Deserialize layout_json if it came back as a string (RETURNING quirk)."""
    if isinstance(d.get("layout_json"), str):
        try:
            d["layout_json"] = json.loads(d["layout_json"])
        except (json.JSONDecodeError, ValueError):
            d["layout_json"] = {}
    return d
