"""Pydantic schemas for job_opening_projects."""
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class ProjectResponse(BaseSchema):
    """Response schema for a job opening resume project entry."""

    id: int
    resume_id: int
    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technologies: Optional[list[str]] = None
    display_order: int = 0


class ProjectCreate(BaseSchema):
    """Request schema for creating a job opening project entry."""

    name: str
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technologies: Optional[list[str]] = None
    display_order: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)

    @field_validator("url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def sanitize_dates(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("technologies", mode="before")
    @classmethod
    def sanitize_technologies(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("technologies must be a list")
        return [sanitize_text(t, max_length=255) for t in v]


class ProjectUpdate(BaseSchema):
    """Request schema for partial update of a job opening project entry."""

    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    technologies: Optional[list[str]] = None
    display_order: Optional[int] = None

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)

    @field_validator("url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def sanitize_dates(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("technologies", mode="before")
    @classmethod
    def sanitize_technologies(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("technologies must be a list")
        return [sanitize_text(t, max_length=255) for t in v]
