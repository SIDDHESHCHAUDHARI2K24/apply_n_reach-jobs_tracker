"""Pydantic schemas for the opening_ingestion feature."""
from datetime import datetime
from enum import Enum

from app.features.core.base_model import BaseSchema
from app.features.job_tracker.schemas import ExtractedJobDetails


class ExtractionRunStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class ExtractionRunResponse(BaseSchema):
    id: int
    opening_id: int
    status: ExtractionRunStatus
    attempt_number: int
    started_at: datetime | None = None
    completed_at: datetime | None = None
    next_retry_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime


class ExtractionRefreshResponse(BaseSchema):
    message: str
    run_id: int


class ExtractedDetailsResponse(BaseSchema):
    # All ExtractedJobDetails fields
    job_title: str | None = None
    company_name: str | None = None
    location: str | None = None
    employment_type: str | None = None
    salary_range: str | None = None
    description_summary: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    experience_level: str | None = None
    posted_date: str | None = None
    application_deadline: str | None = None
    extractor_model: str | None = None
    source_url: str | None = None
    # Provenance
    extraction_run_id: int
    opening_id: int
    schema_version: int
    extracted_at: datetime
