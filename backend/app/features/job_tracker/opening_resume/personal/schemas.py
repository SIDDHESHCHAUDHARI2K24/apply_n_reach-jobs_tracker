"""Pydantic schemas for job_opening_personal."""
from typing import Optional

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text
from pydantic import field_validator


class PersonalResponse(BaseSchema):
    """Response schema for job opening resume personal section."""

    id: int
    resume_id: int
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None


class PersonalUpdate(BaseSchema):
    """Request schema for upserting job opening resume personal section (all fields optional)."""

    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None

    @field_validator("full_name", "email", "phone", "location", mode="before")
    @classmethod
    def sanitize_text_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("linkedin_url", "github_url", "portfolio_url", mode="before")
    @classmethod
    def sanitize_url_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("summary", mode="before")
    @classmethod
    def sanitize_summary(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=5000)
