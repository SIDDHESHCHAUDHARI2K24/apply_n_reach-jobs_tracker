"""Shared helpers for import ownership validation and duplicate detection."""
import asyncpg


async def validate_source_ownership(
    conn: asyncpg.Connection,
    source_table: str,
    source_ids: list[int],
    user_id: int,
) -> tuple[list[int], list[int]]:
    """Verify source_ids belong to the authenticated user's master profile.

    SECURITY: source_table is developer-provided (hardcoded), never user input.
    The JOIN through user_profiles ensures ownership, not just existence.

    Returns:
        (valid_ids, not_found_ids)
    """
    rows = await conn.fetch(
        f"SELECT s.id FROM {source_table} s "
        f"JOIN user_profiles up ON s.profile_id = up.id "
        f"WHERE s.id = ANY($1) AND up.user_id = $2",
        source_ids, user_id
    )
    valid_ids = [row["id"] for row in rows]
    not_found_ids = [sid for sid in source_ids if sid not in valid_ids]
    return valid_ids, not_found_ids


async def get_already_imported(
    conn: asyncpg.Connection,
    target_table: str,
    job_profile_id: int,
    source_column: str,
    source_ids: list[int],
) -> list[int]:
    """Check which source_ids are already imported into the target table.

    SECURITY: target_table and source_column are developer-provided (hardcoded).

    Returns:
        List of source_ids already present in target_table.
    """
    rows = await conn.fetch(
        f"SELECT {source_column} FROM {target_table} "
        f"WHERE job_profile_id = $1 AND {source_column} = ANY($2)",
        job_profile_id, source_ids
    )
    return [row[source_column] for row in rows]
