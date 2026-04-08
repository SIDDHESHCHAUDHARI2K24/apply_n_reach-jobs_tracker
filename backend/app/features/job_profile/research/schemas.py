"""Pydantic schemas for the job_profile research sub-feature."""
from datetime import datetime
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class JPResearchCreate(BaseSchema):
    """Request schema for creating a job profile research entry."""

    paper_name: str
    publication_link: str
    description: str = ""

    @field_validator("paper_name", mode="before")
    @classmethod
    def sanitize_paper_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("publication_link", mode="before")
    @classmethod
    def sanitize_publication_link(cls, v):
        return sanitize_text(v, max_length=2048)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        return sanitize_text(v, max_length=10000)


class JPResearchUpdate(BaseSchema):
    """Request schema for partially updating a job profile research entry."""

    paper_name: Optional[str] = None
    publication_link: Optional[str] = None
    description: Optional[str] = None

    @field_validator("paper_name", mode="before")
    @classmethod
    def sanitize_paper_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("publication_link", mode="before")
    @classmethod
    def sanitize_publication_link(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=10000)


class JPResearchResponse(BaseSchema):
    """Response schema for a job profile research entry."""

    id: int
    job_profile_id: int
    source_research_id: Optional[int] = None
    paper_name: str
    publication_link: str
    description: str
    created_at: datetime
    updated_at: datetime
