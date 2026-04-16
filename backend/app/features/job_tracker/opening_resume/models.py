"""SQL helpers for job_opening_resumes root table."""
import asyncpg


async def get_resume_by_opening(
    conn: asyncpg.Connection, opening_id: int
) -> asyncpg.Record | None:
    """Fetch a resume row by opening_id."""
    return await conn.fetchrow(
        "SELECT * FROM job_opening_resumes WHERE opening_id = $1", opening_id
    )
