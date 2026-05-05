"""Service layer for opening resume LaTeX rendering."""

from __future__ import annotations

import json
import re

import asyncpg
from fastapi import HTTPException, status

from app.features.job_tracker.opening_resume import service as opening_resume_service
from app.features.job_tracker.opening_resume.latex_resume import models
from app.features.job_tracker.opening_resume.latex_resume.renderer import (
    LatexCompileError,
    render_pdf,
)
from app.features.job_tracker.opening_resume.latex_resume.template_builder import (
    build_latex_document,
)
from app.features.job_profile.latex_resume.schemas import ResumeLayoutOptions


def _row_to_dict(row: asyncpg.Record) -> dict:
    """Convert asyncpg row values to native dict values."""
    data = dict(row)
    for key, value in data.items():
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.startswith(("[", "{")):
                try:
                    data[key] = json.loads(value)
                except (json.JSONDecodeError, ValueError):
                    pass
    return data


def _build_filename_stem(
    full_name: str | None,
    role_name: str | None,
    opening_id: int,
    resume_id: int | None = None,
) -> str:
    """Build a filename stem for render/download flows.

    - Render flow may include human-readable name/role parts.
    - Download flow should be deterministic from immutable IDs.
    """
    if not full_name and not role_name:
        suffix = f"_resume_{resume_id}" if resume_id is not None else "_resume"
        return f"opening_{opening_id}{suffix}"

    name_parts = (full_name or "").strip().split()
    if len(name_parts) >= 2:
        first = name_parts[0]
        last = name_parts[-1]
    elif name_parts:
        first = name_parts[0]
        last = ""
    else:
        first = "resume"
        last = ""

    role_part = (role_name or "").strip() or "opening"
    stem = "_".join(
        [part for part in [f"opening_{opening_id}", first, last, role_part] if part]
    ).lower()
    stem = stem.replace(" ", "_")
    stem = re.sub(r"[^\w\-]", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    return stem or f"opening_{opening_id}_resume"


async def aggregate_opening_resume_data(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    resume_id: int,
) -> dict:
    """Fetch opening resume sections and map them to the LaTeX template shape."""
    opening_row = await conn.fetchrow(
        """
        SELECT o.id, o.role_name
        FROM job_openings o
        JOIN job_opening_resumes r ON r.opening_id = o.id
        WHERE o.id = $1 AND o.user_id = $2 AND r.id = $3
        """,
        opening_id,
        user_id,
        resume_id,
    )
    if opening_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    personal_row = await conn.fetchrow(
        """
        SELECT full_name, email, phone, location, summary,
               linkedin_url, github_url, portfolio_url
        FROM job_opening_personal
        WHERE resume_id = $1
        """,
        resume_id,
    )

    education_rows = await conn.fetch(
        """
        SELECT
            institution AS university_name,
            field_of_study AS major,
            degree AS degree_type,
            start_date AS start_month_year,
            end_date AS end_month_year,
            bullet_points
        FROM job_opening_education
        WHERE resume_id = $1
        ORDER BY display_order ASC, id ASC
        """,
        resume_id,
    )

    experience_rows = await conn.fetch(
        """
        SELECT
            title AS role_title,
            company AS company_name,
            location,
            start_date AS start_month_year,
            CASE
                WHEN is_current THEN NULL
                ELSE end_date
            END AS end_month_year,
            description AS context,
            bullet_points,
            work_sample_links
        FROM job_opening_experience
        WHERE resume_id = $1
        ORDER BY display_order ASC, id ASC
        """,
        resume_id,
    )

    project_rows = await conn.fetch(
        """
        SELECT
            name AS project_name,
            description,
            start_date AS start_month_year,
            end_date AS end_month_year,
            reference_links,
            technologies
        FROM job_opening_projects
        WHERE resume_id = $1
        ORDER BY display_order ASC, id ASC
        """,
        resume_id,
    )

    research_rows = await conn.fetch(
        """
        SELECT
            title AS paper_name,
            url AS publication_link,
            description,
            publication AS journal,
            published_date AS year
        FROM job_opening_research
        WHERE resume_id = $1
        ORDER BY display_order ASC, id ASC
        """,
        resume_id,
    )

    certification_rows = await conn.fetch(
        """
        SELECT
            name AS certification_name,
            url AS verification_link
        FROM job_opening_certifications
        WHERE resume_id = $1
        ORDER BY display_order ASC, id ASC
        """,
        resume_id,
    )

    skill_rows = await conn.fetch(
        """
        SELECT
            category AS kind,
            name,
            display_order AS sort_order
        FROM job_opening_skills
        WHERE resume_id = $1
        ORDER BY display_order ASC, id ASC
        """,
        resume_id,
    )

    return {
        "opening": dict(opening_row),
        "personal": dict(personal_row) if personal_row else {},
        "job_meta": {"target_role": opening_row["role_name"]},
        "educations": [_row_to_dict(row) for row in education_rows],
        "experiences": [_row_to_dict(row) for row in experience_rows],
        "projects": [_row_to_dict(row) for row in project_rows],
        "researches": [_row_to_dict(row) for row in research_rows],
        "certifications": [_row_to_dict(row) for row in certification_rows],
        "skill_items": [_row_to_dict(row) for row in skill_rows],
    }


async def render_resume(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
    layout: ResumeLayoutOptions | None,
) -> dict:
    """Render and upsert an opening resume PDF and LaTeX source."""
    if layout is None:
        layout = ResumeLayoutOptions()

    resume_id = await opening_resume_service._get_resume_id(conn, user_id, opening_id)
    profile_data = await aggregate_opening_resume_data(conn, user_id, opening_id, resume_id)

    latex_source = build_latex_document(profile_data, layout)
    opening = profile_data["opening"]
    personal = profile_data["personal"]
    filename_stem = _build_filename_stem(
        personal.get("full_name"),
        opening.get("role_name"),
        opening_id,
    )

    try:
        pdf_bytes = render_pdf(latex_source, filename_stem=filename_stem)
    except LatexCompileError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LaTeX compilation failed: {exc}. Log: {exc.log_tail[:500] if exc.log_tail else 'no log'}",
        ) from exc

    row = await conn.fetchrow(
        f"""
        INSERT INTO {models.TABLE_NAME} (resume_id, latex_source, pdf_bytes, template_name)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (resume_id) DO UPDATE SET
            latex_source = EXCLUDED.latex_source,
            pdf_bytes = EXCLUDED.pdf_bytes,
            template_name = EXCLUDED.template_name,
            updated_at = NOW()
        RETURNING
            resume_id,
            template_name,
            updated_at,
            char_length(latex_source) AS latex_length,
            octet_length(pdf_bytes) AS pdf_size_bytes
        """,
        resume_id,
        latex_source,
        pdf_bytes,
        models.DEFAULT_TEMPLATE_NAME,
    )
    return dict(row)


async def get_latex_resume_metadata(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> dict | None:
    """Fetch metadata for the rendered opening resume."""
    resume_id = await opening_resume_service._get_resume_id(conn, user_id, opening_id)
    row = await conn.fetchrow(
        f"""
        SELECT
            resume_id,
            template_name,
            updated_at,
            char_length(latex_source) AS latex_length,
            octet_length(pdf_bytes) AS pdf_size_bytes
        FROM {models.TABLE_NAME}
        WHERE resume_id = $1
        """,
        resume_id,
    )
    if row is None:
        return None
    return dict(row)


async def get_resume_pdf(
    conn: asyncpg.Connection,
    user_id: int,
    opening_id: int,
) -> tuple[bytes, str] | None:
    """Fetch rendered PDF bytes and deterministic filename stem."""
    resume_id = await opening_resume_service._get_resume_id(conn, user_id, opening_id)
    row = await conn.fetchrow(
        f"""
        SELECT
            rr.pdf_bytes,
            o.id AS opening_id,
            rr.resume_id
        FROM {models.TABLE_NAME} rr
        JOIN job_opening_resumes r ON r.id = rr.resume_id
        JOIN job_openings o ON o.id = r.opening_id
        WHERE rr.resume_id = $1 AND o.user_id = $2 AND o.id = $3
        """,
        resume_id,
        user_id,
        opening_id,
    )
    if row is None:
        return None

    filename_stem = _build_filename_stem(
        None,
        None,
        row["opening_id"],
        row["resume_id"],
    )
    return row["pdf_bytes"], filename_stem

