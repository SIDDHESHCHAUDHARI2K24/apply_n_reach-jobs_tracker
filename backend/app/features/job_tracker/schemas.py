"""Pydantic schemas for the job_tracker feature."""
from app.features.core.base_model import BaseSchema


class ExtractedJobDetails(BaseSchema):
    """Schema representing structured job details extracted from a job posting.

    Fields are intentionally not sanitized — this schema is used internally by
    the ingestion pipeline and all values are AI-generated, not raw user input.
    """

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
