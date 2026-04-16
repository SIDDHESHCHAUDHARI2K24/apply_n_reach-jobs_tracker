"""Pydantic schemas for job_opening_education."""
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class EducationResponse(BaseSchema):
    """Response schema for a job opening resume education entry."""

    id: int
    resume_id: int
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0


class EducationCreate(BaseSchema):
    """Request schema for creating a job opening education entry."""

    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0

    @field_validator("institution", mode="before")
    @classmethod
    def sanitize_institution(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("degree", "field_of_study", "grade", mode="before")
    @classmethod
    def sanitize_short_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def sanitize_dates(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)


class EducationUpdate(BaseSchema):
    """Request schema for partial update of a job opening education entry."""

    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    grade: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None

    @field_validator("institution", mode="before")
    @classmethod
    def sanitize_institution(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("degree", "field_of_study", "grade", mode="before")
    @classmethod
    def sanitize_short_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def sanitize_dates(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)
