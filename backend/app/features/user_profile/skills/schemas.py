"""Pydantic schemas for the skills sub-feature."""
from typing import Literal, Optional
from datetime import datetime

from pydantic import field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class SkillItemCreate(BaseSchema):
    """Schema for a single skill item in a PATCH /profile/skills request."""

    kind: Literal["technical", "competency"]
    name: str
    sort_order: int = 0

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, v):
        """Strip HTML and enforce 100 char limit on skill name."""
        return sanitize_text(v, max_length=100)


class SkillsUpdate(BaseSchema):
    """Request body for PATCH /profile/skills — replaces the full skill set."""

    skills: list[SkillItemCreate] = []


class SkillItemResponse(BaseSchema):
    """Response schema for a single skill item."""

    id: int
    profile_id: int
    kind: str
    name: str
    sort_order: int
    created_at: datetime
