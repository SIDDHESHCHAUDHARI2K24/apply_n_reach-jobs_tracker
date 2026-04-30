"""Pydantic schemas for the job_profile personal sub-feature."""
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class JPPersonalDetailsCreate(BaseSchema):
    """Request schema for creating or replacing job profile personal details."""

    full_name: str
    email: EmailStr
    linkedin_url: str
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def sanitize_full_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("linkedin_url", mode="before")
    @classmethod
    def sanitize_linkedin_url(cls, v):
        return sanitize_text(v, max_length=2048)

    @field_validator("github_url", mode="before")
    @classmethod
    def sanitize_github_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("portfolio_url", mode="before")
    @classmethod
    def sanitize_portfolio_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("summary", mode="before")
    @classmethod
    def sanitize_summary(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2000)

    @field_validator("location", mode="before")
    @classmethod
    def sanitize_location(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("phone", mode="before")
    @classmethod
    def sanitize_phone(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)


class JPPersonalDetailsUpdate(BaseSchema):
    """Request schema for partial update of job profile personal details (all fields optional)."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def sanitize_full_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("linkedin_url", mode="before")
    @classmethod
    def sanitize_linkedin_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("github_url", mode="before")
    @classmethod
    def sanitize_github_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("portfolio_url", mode="before")
    @classmethod
    def sanitize_portfolio_url(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("summary", mode="before")
    @classmethod
    def sanitize_summary(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=2000)

    @field_validator("location", mode="before")
    @classmethod
    def sanitize_location(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("phone", mode="before")
    @classmethod
    def sanitize_phone(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=50)


class JPPersonalDetailsResponse(BaseSchema):
    """Response schema for job profile personal details."""

    id: int
    job_profile_id: int
    source_personal_id: Optional[int] = None
    full_name: str
    email: str
    linkedin_url: str
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
