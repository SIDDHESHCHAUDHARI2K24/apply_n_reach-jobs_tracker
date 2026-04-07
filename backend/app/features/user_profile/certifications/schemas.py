"""Pydantic schemas for the certifications sub-feature."""
from datetime import datetime
from typing import Optional

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text
from pydantic import field_validator


class CertificationCreate(BaseSchema):
    """Request schema for creating or updating a certification entry."""

    certification_name: str
    verification_link: str

    @field_validator("certification_name", mode="before")
    @classmethod
    def sanitize_certification_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("verification_link", mode="before")
    @classmethod
    def sanitize_verification_link(cls, v):
        return sanitize_text(str(v), max_length=2048)


class CertificationUpdate(BaseSchema):
    """Request schema for partially updating a certification entry (all fields optional)."""

    certification_name: Optional[str] = None
    verification_link: Optional[str] = None

    @field_validator("certification_name", mode="before")
    @classmethod
    def sanitize_certification_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("verification_link", mode="before")
    @classmethod
    def sanitize_verification_link(cls, v):
        if v is None:
            return None
        return sanitize_text(str(v), max_length=2048)


class CertificationResponse(BaseSchema):
    """Response schema for a certification entry."""

    id: int
    profile_id: int
    certification_name: str
    verification_link: str
    created_at: datetime
    updated_at: datetime
