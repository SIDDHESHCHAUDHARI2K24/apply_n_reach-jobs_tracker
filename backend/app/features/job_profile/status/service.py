"""Service functions for job_profile status transitions."""
import asyncpg
from fastapi import HTTPException

from app.features.job_profile.status.schemas import JobProfileStatus


TRANSITION_MATRIX: dict[JobProfileStatus, set[JobProfileStatus]] = {
    JobProfileStatus.Draft: {JobProfileStatus.Active, JobProfileStatus.Archived},
    JobProfileStatus.Active: {JobProfileStatus.Archived},
    JobProfileStatus.Archived: {JobProfileStatus.Active},
}


async def transition_job_profile_status(
    conn: asyncpg.Connection,
    job_profile: asyncpg.Record,
    to_status: JobProfileStatus,
) -> asyncpg.Record:
    """Transition a job profile to a new status with explicit rules."""
    current_status = JobProfileStatus(job_profile["status"])
    if current_status == to_status:
        return job_profile

    allowed = TRANSITION_MATRIX.get(current_status, set())
    if to_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status.value} to {to_status.value}",
        )

    row = await conn.fetchrow(
        """
        UPDATE job_profiles
        SET status = $1, updated_at = NOW()
        WHERE id = $2 AND user_id = $3
        RETURNING *
        """,
        to_status.value,
        job_profile["id"],
        job_profile["user_id"],
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Job profile not found")
    return row

