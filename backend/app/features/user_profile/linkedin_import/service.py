"""Service for LinkedIn profile import — atomic replace-all."""
import json

import asyncpg
from fastapi import HTTPException, status

from app.features.user_profile.linkedin_import.schemas import MappedLinkedInProfile


async def replace_profile_from_linkedin(
    conn: asyncpg.Connection,
    profile_id: int,
    mapped: MappedLinkedInProfile,
) -> dict[str, int]:
    """Atomically replace all user_profile sections with LinkedIn data.

    Deletes existing data for all 6 sections, then inserts the mapped data.
    Returns a dict of section -> count imported.
    """
    counts = {}

    async with conn.transaction():
        # 1. Personal details — upsert
        if mapped.personal:
            p = mapped.personal
            await conn.execute(
                """
                INSERT INTO personal_details (profile_id, full_name, email, linkedin_url, github_url, portfolio_url)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (profile_id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    email = EXCLUDED.email,
                    linkedin_url = EXCLUDED.linkedin_url,
                    github_url = EXCLUDED.github_url,
                    portfolio_url = EXCLUDED.portfolio_url,
                    updated_at = NOW()
                """,
                profile_id, p.full_name, p.email, p.linkedin_url, p.github_url, p.portfolio_url,
            )
            counts["personal"] = 1

        # 2. Education — delete all then insert
        await conn.execute("DELETE FROM educations WHERE profile_id = $1", profile_id)
        for edu in mapped.educations:
            await conn.execute(
                """
                INSERT INTO educations (profile_id, university_name, major, degree_type,
                    start_month_year, end_month_year, bullet_points, reference_links)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
                """,
                profile_id, edu.university_name, edu.major, edu.degree_type,
                edu.start_month_year, edu.end_month_year or None,
                json.dumps(edu.bullet_points), json.dumps(edu.reference_links),
            )
        counts["education"] = len(mapped.educations)

        # 3. Experience — delete all then insert
        await conn.execute("DELETE FROM experiences WHERE profile_id = $1", profile_id)
        for exp in mapped.experiences:
            await conn.execute(
                """
                INSERT INTO experiences (profile_id, role_title, company_name,
                    start_month_year, end_month_year, context, work_sample_links, bullet_points)
                VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb, $8::jsonb)
                """,
                profile_id, exp.role_title, exp.company_name,
                exp.start_month_year, exp.end_month_year or None,
                exp.context, json.dumps(exp.work_sample_links), json.dumps(exp.bullet_points),
            )
        counts["experience"] = len(mapped.experiences)

        # 4. Projects — delete all then insert
        await conn.execute("DELETE FROM projects WHERE profile_id = $1", profile_id)
        for proj in mapped.projects:
            await conn.execute(
                """
                INSERT INTO projects (profile_id, project_name, description,
                    start_month_year, end_month_year, reference_links)
                VALUES ($1, $2, $3, $4, $5, $6::jsonb)
                """,
                profile_id, proj.project_name, proj.description,
                proj.start_month_year, proj.end_month_year or None,
                json.dumps(proj.reference_links),
            )
        counts["projects"] = len(mapped.projects)

        # 5. Certifications — delete all then insert
        await conn.execute("DELETE FROM certifications WHERE profile_id = $1", profile_id)
        for cert in mapped.certifications:
            await conn.execute(
                """
                INSERT INTO certifications (profile_id, certification_name, verification_link)
                VALUES ($1, $2, $3)
                """,
                profile_id, cert.certification_name, cert.verification_link,
            )
        counts["certifications"] = len(mapped.certifications)

        # 6. Skills — delete all then insert
        await conn.execute("DELETE FROM skill_items WHERE profile_id = $1", profile_id)
        for skill in mapped.skills:
            await conn.execute(
                """
                INSERT INTO skill_items (profile_id, kind, name, sort_order)
                VALUES ($1, $2, $3, $4)
                """,
                profile_id, skill.kind, skill.name, skill.sort_order,
            )
        counts["skills"] = len(mapped.skills)

    return counts
