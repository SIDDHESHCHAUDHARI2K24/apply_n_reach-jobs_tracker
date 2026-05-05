"""Pydantic schemas for the opening_ingestion feature."""
from datetime import datetime
from enum import Enum

from pydantic import Field

from app.features.core.base_model import BaseSchema


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


class ManualExtractedDetailsCreate(BaseSchema):
    """User-provided snapshot for tailoring when crawl/LLM extraction is unavailable."""

    job_title: str | None = None
    company_name: str | None = None
    location: str | None = None
    employment_type: str | None = None
    description_summary: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    experience_level: str | None = None
    posted_date: str | None = None
    application_deadline: str | None = None
    source_url: str | None = None
    role_summary: str | None = None
    technical_keywords: list[str] | None = None
    sector_keywords: list[str] | None = None
    business_sectors: list[str] | None = None
    problem_being_solved: str | None = None
    useful_experiences: list[str] | None = None
    extra_raw: dict[str, object] | None = Field(
        default=None,
        description="Merged into stored raw_payload beside source marker",
    )


class ExtractedDetailsResponse(BaseSchema):
    # All ExtractedJobDetails fields
    job_title: str | None = None
    company_name: str | None = None
    location: str | None = None
    employment_type: str | None = None
    description_summary: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    experience_level: str | None = None
    posted_date: str | None = None
    application_deadline: str | None = None
    extractor_model: str | None = None
    source_url: str | None = None
    role_summary: str | None = None
    technical_keywords: list[str] | None = None
    sector_keywords: list[str] | None = None
    business_sectors: list[str] | None = None
    problem_being_solved: str | None = None
    useful_experiences: list[str] | None = None
    # Provenance
    extraction_run_id: int
    opening_id: int
    schema_version: int
    extracted_at: datetime
