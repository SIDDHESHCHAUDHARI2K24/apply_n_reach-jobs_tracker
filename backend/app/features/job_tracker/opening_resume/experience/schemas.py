"""Pydantic schemas for job_opening_experience."""
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class ExperienceResponse(BaseSchema):
    """Response schema for a job opening resume experience entry."""

    id: int
    resume_id: int
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullet_points: list[str] = []
    work_sample_links: list[str] = []
    display_order: int = 0


class ExperienceCreate(BaseSchema):
    """Request schema for creating a job opening experience entry."""

    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    bullet_points: list[str] = []
    work_sample_links: list[str] = []
    display_order: int = 0

    @field_validator("company", "title", mode="before")
    @classmethod
    def sanitize_required(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("location", mode="before")
    @classmethod
    def sanitize_location(cls, v):
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

    @field_validator("bullet_points", mode="before")
    @classmethod
    def sanitize_bullets(cls, v):
        if not isinstance(v, list):
            raise ValueError("bullet_points must be a list")
        return [sanitize_text(item, max_length=500) for item in v]

    @field_validator("work_sample_links", mode="before")
    @classmethod
    def sanitize_work_sample_links(cls, v):
        if not isinstance(v, list):
            raise ValueError("work_sample_links must be a list")
        if len(v) > 1:
            raise ValueError("Only one work sample link allowed per entry")
        return [sanitize_text(str(item), max_length=2048) for item in v]


class ExperienceUpdate(BaseSchema):
    """Request schema for partial update of a job opening experience entry."""

    company: Optional[str] = None
    title: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: Optional[bool] = None
    description: Optional[str] = None
    bullet_points: Optional[list[str]] = None
    work_sample_links: Optional[list[str]] = None
    display_order: Optional[int] = None

    @field_validator("company", "title", mode="before")
    @classmethod
    def sanitize_required(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("location", mode="before")
    @classmethod
    def sanitize_location(cls, v):
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

    @field_validator("bullet_points", mode="before")
    @classmethod
    def sanitize_bullets_upd(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("bullet_points must be a list")
        return [sanitize_text(item, max_length=500) for item in v]

    @field_validator("work_sample_links", mode="before")
    @classmethod
    def sanitize_work_sample_links_upd(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("work_sample_links must be a list")
        if len(v) > 1:
            raise ValueError("Only one work sample link allowed per entry")
        return [sanitize_text(str(item), max_length=2048) for item in v]
