"""Pydantic schemas for the job_profile projects sub-feature."""
import re
from datetime import datetime
from typing import Optional

from pydantic import field_validator, model_validator

from app.features.core.base_model import BaseSchema
from app.features.user_profile.validators import sanitize_text

_MONTH_YEAR_RE = re.compile(r"^(0[1-9]|1[0-2])\/\d{4}$")


def _parse_month_year(s: str) -> tuple[int, int]:
    """Parse MM/YYYY string into (year, month) tuple for comparison."""
    month, year = s.split("/")
    return int(year), int(month)


class JPProjectCreate(BaseSchema):
    """Request schema for creating a job profile project entry."""

    project_name: str
    description: str = ""
    start_month_year: Optional[str] = None
    end_month_year: Optional[str] = None
    reference_links: list[str] = []

    @field_validator("project_name", mode="before")
    @classmethod
    def sanitize_project_name(cls, v):
        return sanitize_text(v, max_length=255)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return ""
        return sanitize_text(v, max_length=10000)

    @field_validator("start_month_year", mode="before")
    @classmethod
    def validate_start(cls, v):
        if v is None:
            return None
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("start_month_year must be MM/YYYY format")
        return v

    @field_validator("end_month_year", mode="before")
    @classmethod
    def validate_end(cls, v):
        if v is None:
            return None
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("end_month_year must be MM/YYYY format")
        return v

    @field_validator("reference_links", mode="before")
    @classmethod
    def sanitize_links(cls, v):
        if not isinstance(v, list):
            raise ValueError("reference_links must be a list")
        return [sanitize_text(str(item), max_length=2048) for item in v]

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.start_month_year and self.end_month_year:
            start = _parse_month_year(self.start_month_year)
            end = _parse_month_year(self.end_month_year)
            if end < start:
                raise ValueError("end_month_year must be >= start_month_year")
        return self


class JPProjectUpdate(BaseSchema):
    """Request schema for partial update of a job profile project entry (all fields optional)."""

    project_name: Optional[str] = None
    description: Optional[str] = None
    start_month_year: Optional[str] = None
    end_month_year: Optional[str] = None
    reference_links: Optional[list[str]] = None

    @field_validator("project_name", mode="before")
    @classmethod
    def sanitize_project_name(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=255)

    @field_validator("description", mode="before")
    @classmethod
    def sanitize_description(cls, v):
        if v is None:
            return None
        return sanitize_text(v, max_length=10000)

    @field_validator("start_month_year", mode="before")
    @classmethod
    def validate_start(cls, v):
        if v is None:
            return None
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("start_month_year must be MM/YYYY format")
        return v

    @field_validator("end_month_year", mode="before")
    @classmethod
    def validate_end(cls, v):
        if v is None:
            return None
        if not _MONTH_YEAR_RE.match(str(v)):
            raise ValueError("end_month_year must be MM/YYYY format")
        return v

    @field_validator("reference_links", mode="before")
    @classmethod
    def sanitize_links(cls, v):
        if v is None:
            return None
        if not isinstance(v, list):
            raise ValueError("reference_links must be a list")
        return [sanitize_text(str(item), max_length=2048) for item in v]

    @model_validator(mode="after")
    def validate_date_order(self):
        if self.start_month_year and self.end_month_year:
            start = _parse_month_year(self.start_month_year)
            end = _parse_month_year(self.end_month_year)
            if end < start:
                raise ValueError("end_month_year must be >= start_month_year")
        return self


class JPProjectResponse(BaseSchema):
    """Response schema for a job profile project entry."""

    id: int
    job_profile_id: int
    source_project_id: Optional[int] = None
    project_name: str
    description: str
    start_month_year: Optional[str] = None
    end_month_year: Optional[str] = None
    reference_links: list[str] = []
    created_at: datetime
    updated_at: datetime
