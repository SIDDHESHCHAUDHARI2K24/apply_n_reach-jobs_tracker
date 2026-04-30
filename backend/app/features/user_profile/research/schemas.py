"""Pydantic schemas for the research sub-feature."""
from datetime import datetime
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class ResearchCreate(BaseSchema):
    """Request schema for creating or updating a research entry."""

    paper_name: str
    publication_link: str
    description: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None

    @field_validator("paper_name", mode="before")
    @classmethod
    def sanitize_paper_name(cls, v):
        return sanitize_text(v, max_length=500)

    @field_validator("publication_link", mode="before")
    @classmethod
    def sanitize_publication_link(cls, v):
        return sanitize_text(str(v), max_length=2048)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return v
        return sanitize_text(v, max_length=2000)

    @field_validator("journal", mode="before")
    @classmethod
    def sanitize_journal(cls, v):
        if v is None:
            return v
        return sanitize_text(v, max_length=500)

    @field_validator("year", mode="before")
    @classmethod
    def sanitize_year(cls, v):
        if v is None:
            return v
        return sanitize_text(v, max_length=10)


class ResearchUpdate(BaseSchema):
    """Request schema for partially updating a research entry (all fields optional)."""

    paper_name: Optional[str] = None
    publication_link: Optional[str] = None
    description: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None

    @field_validator("paper_name", mode="before")
    @classmethod
    def sanitize_paper_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=500)

    @field_validator("publication_link", mode="before")
    @classmethod
    def sanitize_publication_link(cls, v):
        if v is None:
            return None
        return sanitize_text(str(v), max_length=2048)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2000)

    @field_validator("journal", mode="before")
    @classmethod
    def sanitize_journal(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=500)

    @field_validator("year", mode="before")
    @classmethod
    def sanitize_year(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=10)


class ResearchResponse(BaseSchema):
    """Response schema for a research entry."""

    id: int
    profile_id: int
    paper_name: str
    publication_link: str
    description: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[str] = None
    created_at: datetime
    updated_at: datetime
