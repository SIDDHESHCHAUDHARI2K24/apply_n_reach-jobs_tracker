"""Pydantic schemas for the personal sub-feature (UserProfile + PersonalDetails)."""
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, field_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text


class UserProfileCreatedResponse(BaseSchema):
    """Response schema for POST /profile — minimal, no nested sections."""

    id: int
    user_id: int
    created_at: datetime


class PersonalDetailsCreate(BaseSchema):
    """Request schema for PATCH /profile/personal."""

    full_name: str
    email: EmailStr
    linkedin_url: str
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML and enforce 255 char limit on full_name."""
        return sanitize_text(v, max_length=255)

    @field_validator("linkedin_url", mode="before")
    @classmethod
    def sanitize_linkedin_url(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML from linkedin_url."""
        return sanitize_text(v, max_length=2048)

    @field_validator("github_url", mode="before")
    @classmethod
    def sanitize_github_url(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML from github_url."""
        return sanitize_text(v, max_length=2048)

    @field_validator("portfolio_url", mode="before")
    @classmethod
    def sanitize_portfolio_url(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML from portfolio_url."""
        return sanitize_text(v, max_length=2048)

    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("summary", mode="before")
    @classmethod
    def sanitize_summary(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML and enforce 5000 char limit on summary."""
        return sanitize_text(v, max_length=5000)

    @field_validator("location", mode="before")
    @classmethod
    def sanitize_location(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML and enforce 255 char limit on location."""
        return sanitize_text(v, max_length=255)

    @field_validator("phone", mode="before")
    @classmethod
    def sanitize_phone(cls, v: Optional[str]) -> Optional[str]:
        """Strip HTML and enforce 50 char limit on phone."""
        return sanitize_text(v, max_length=50)


class PersonalDetailsUpdate(BaseSchema):
    """Request schema for partial PATCH /profile/personal (all fields optional)."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    @field_validator("full_name", mode="before")
    @classmethod
    def sanitize_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("linkedin_url", mode="before")
    @classmethod
    def sanitize_linkedin_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("github_url", mode="before")
    @classmethod
    def sanitize_github_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    @field_validator("portfolio_url", mode="before")
    @classmethod
    def sanitize_portfolio_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=2048)

    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("summary", mode="before")
    @classmethod
    def sanitize_summary(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=2000)

    @field_validator("location", mode="before")
    @classmethod
    def sanitize_location(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("phone", mode="before")
    @classmethod
    def sanitize_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return sanitize_text(v, max_length=50)


class PersonalDetailsResponse(BaseSchema):
    """Response schema for GET /profile/personal and PATCH /profile/personal."""

    id: int
    profile_id: int
    full_name: str
    email: str
    linkedin_url: str
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None


class ProfileSummaryResponse(BaseSchema):
    """Response schema for GET /profile/summary."""

    personal_details_exists: bool
    education_count: int
    experience_count: int
    projects_count: int
    research_count: int
    certifications_count: int
    skills_count: int
