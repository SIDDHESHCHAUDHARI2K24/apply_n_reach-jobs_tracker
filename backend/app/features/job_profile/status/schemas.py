"""Schemas for job_profile status transitions."""
from enum import Enum


class JobProfileStatus(str, Enum):
    """Supported job profile states."""

    Draft = "draft"
    Active = "active"
    Archived = "archived"

