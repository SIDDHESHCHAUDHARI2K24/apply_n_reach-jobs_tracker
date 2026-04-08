"""Pydantic schemas for the job_profile skills sub-feature."""
from datetime import datetime
from typing import Literal

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class JPSkillItemCreate(BaseSchema):
    """Schema for a single skill item in a replace-all request."""

    kind: Literal["technical", "competency"]
    name: str
    sort_order: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        return sanitize_text(str(v), max_length=255)


class JPSkillsUpdate(BaseSchema):
    """Replace-all: provide the complete desired list of skills."""

    skills: list[JPSkillItemCreate]


class JPSkillItemResponse(BaseSchema):
    """Response schema for a single skill item."""

    id: int
    job_profile_id: int
    kind: str
    name: str
    sort_order: int
    created_at: datetime
