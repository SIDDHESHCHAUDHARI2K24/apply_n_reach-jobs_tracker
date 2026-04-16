"""Pydantic schemas for the job_tracker feature."""
from typing import Optional

from app.features.core.base_model import BaseSchema


class ExtractedJobDetails(BaseSchema):
    """Schema representing structured job details extracted from a job posting."""

    job_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    description_summary: Optional[str] = None
    required_skills: Optional[list[str]] = None
    preferred_skills: Optional[list[str]] = None
    experience_level: Optional[str] = None
    posted_date: Optional[str] = None
    application_deadline: Optional[str] = None
    extractor_model: Optional[str] = None
    source_url: Optional[str] = None
