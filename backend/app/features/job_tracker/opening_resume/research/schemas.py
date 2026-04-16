"""Pydantic schemas for job_opening_research."""
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class ResearchResponse(BaseSchema):
    """Response schema for a job opening resume research entry."""

    id: int
    resume_id: int
    title: str
    publication: Optional[str] = None
    published_date: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0


class ResearchCreate(BaseSchema):
    """Request schema for creating a job opening research entry."""

    title: str
    publication: Optional[str] = None
    published_date: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    display_order: int = 0

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("publication", mode="before")
    @classmethod
    def sanitize_publication(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("published_date", mode="before")
    @classmethod
    def sanitize_published_date(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)


class ResearchUpdate(BaseSchema):
    """Request schema for partial update of a job opening research entry."""

    title: Optional[str] = None
    publication: Optional[str] = None
    published_date: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None

    @field_validator("title", mode="before")
    @classmethod
    def sanitize_title(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("publication", mode="before")
    @classmethod
    def sanitize_publication(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("published_date", mode="before")
    @classmethod
    def sanitize_published_date(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)

    @field_validator("url", mode="before")
    @classmethod
    def sanitize_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)
