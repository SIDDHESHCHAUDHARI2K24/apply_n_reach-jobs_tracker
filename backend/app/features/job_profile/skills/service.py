"""Service functions for the job_profile skills sub-feature."""
import asyncpg
from fastapi import HTTPException, status

from app.features.job_profile.skills.models import ensure_jp_skills_schema
from app.features.job_profile.skills.schemas import JPSkillItemCreate
from app.features.job_profile.import_helpers import validate_source_ownership
from app.features.job_profile.import_schemas import ImportResult


async def list_skills(
    conn: asyncpg.Connection, job_profile_id: int
) -> list[asyncpg.Record]:
    """List all skill items for a job profile, ordered by kind then sort_order."""
    await ensure_jp_skills_schema(conn)
    return await conn.fetch(
        "SELECT * FROM job_profile_skill_items WHERE job_profile_id = $1 "
        "ORDER BY kind, sort_order",
        job_profile_id,
    )


async def get_skill(
    conn: asyncpg.Connection, job_profile_id: int, skill_id: int
) -> asyncpg.Record:
    """Fetch a single skill item, verifying ownership via job_profile_id."""
    await ensure_jp_skills_schema(conn)
    row = await conn.fetchrow(
        "SELECT * FROM job_profile_skill_items WHERE id = $1 AND job_profile_id = $2",
        skill_id,
        job_profile_id,
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return row


async def replace_skills(
    conn: asyncpg.Connection,
    job_profile_id: int,
    skills: list[JPSkillItemCreate],
) -> list[asyncpg.Record]:
    """Atomically delete all existing skills and insert the provided list."""
    await ensure_jp_skills_schema(conn)
    async with conn.transaction():
        await conn.execute(
            "DELETE FROM job_profile_skill_items WHERE job_profile_id = $1",
            job_profile_id,
        )
        for skill in skills:
            await conn.execute(
                "INSERT INTO job_profile_skill_items "
                "(job_profile_id, kind, name, sort_order) "
                "VALUES ($1, $2, $3, $4)",
                job_profile_id,
                skill.kind,
                skill.name,
                skill.sort_order,
            )
    return await list_skills(conn, job_profile_id)


async def import_skills_from_profile(
    conn: asyncpg.Connection,
    job_profile_id: int,
    user_id: int,
    source_ids: list[int],
) -> ImportResult:
    """Additive import: append skills not already present, dedup by kind+name."""
    await ensure_jp_skills_schema(conn)

    # 1. Validate source ownership via skill_items -> user_profiles join
    valid_ids, not_found_ids = await validate_source_ownership(
        conn, "skill_items", source_ids, user_id
    )

    if not valid_ids:
        return ImportResult(imported=[], skipped=[], not_found=not_found_ids)

    # 2. Fetch source skill data
    source_rows = await conn.fetch(
        "SELECT * FROM skill_items WHERE id = ANY($1)",
        valid_ids,
    )

    # 3. Get existing skills in job profile (by kind+name) for dedup
    existing = await conn.fetch(
        "SELECT kind, name FROM job_profile_skill_items WHERE job_profile_id = $1",
        job_profile_id,
    )
    existing_pairs = {(r["kind"], r["name"]) for r in existing}

    # 4. Import non-duplicates additively
    imported_ids = []
    skipped_ids = []
    async with conn.transaction():
        for row in source_rows:
            pair = (row["kind"], row["name"])
            if pair in existing_pairs:
                skipped_ids.append(row["id"])
            else:
                await conn.execute(
                    "INSERT INTO job_profile_skill_items "
                    "(job_profile_id, kind, name, sort_order) "
                    "VALUES ($1, $2, $3, $4)",
                    job_profile_id,
                    row["kind"],
                    row["name"],
                    row.get("sort_order", 0),
                )
                imported_ids.append(row["id"])
                existing_pairs.add(pair)

    return ImportResult(
        imported=imported_ids,
        skipped=skipped_ids,
        not_found=not_found_ids,
    )
