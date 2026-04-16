"""Pydantic schemas for job_opening_resumes root."""
from datetime import datetime
from typing import Optional

from app.features.core.base_model import BaseSchema


class ResumeResponse(BaseSchema):
    """Response schema for a job opening resume root row."""

    id: int
    opening_id: int
    source_job_profile_id: Optional[int] = None
    snapshot_at: datetime
    snapshot_version: int
    source_section_count: int
