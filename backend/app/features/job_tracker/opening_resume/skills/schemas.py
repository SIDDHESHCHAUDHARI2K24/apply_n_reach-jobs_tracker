"""Pydantic schemas for job_opening_skills."""
from typing import Optional

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class SkillResponse(BaseSchema):
    """Response schema for a job opening resume skill entry."""

    id: int
    resume_id: int
    category: str
    name: str
    proficiency_level: Optional[str] = None
    display_order: int = 0


class SkillCreate(BaseSchema):
    """Request schema for creating a job opening skill entry."""

    category: str
    name: str
    proficiency_level: Optional[str] = None
    display_order: int = 0

    @field_validator("category", "name", mode="before")
    @classmethod
    def sanitize_required(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("proficiency_level", mode="before")
    @classmethod
    def sanitize_proficiency(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)


class SkillUpdate(BaseSchema):
    """Request schema for partial update of a job opening skill entry."""

    category: Optional[str] = None
    name: Optional[str] = None
    proficiency_level: Optional[str] = None
    display_order: Optional[int] = None

    @field_validator("category", "name", mode="before")
    @classmethod
    def sanitize_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("proficiency_level", mode="before")
    @classmethod
    def sanitize_proficiency(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)
