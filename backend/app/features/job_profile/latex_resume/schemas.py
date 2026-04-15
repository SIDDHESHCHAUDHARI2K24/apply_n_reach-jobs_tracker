"""Pydantic schemas for the latex_resume sub-feature."""
from datetime import datetime
from pydantic import field_validator, model_validator
from app.features.core.base_model import BaseSchema


class ResumeMarginsInches(BaseSchema):
    top: float | None = None
    bottom: float | None = None
    left: float | None = None
    right: float | None = None

    @model_validator(mode="after")
    def all_or_nothing(self):
        values = [self.top, self.bottom, self.left, self.right]
        set_count = sum(v is not None for v in values)
        if set_count not in (0, 4):
            raise ValueError("Either all four margins must be set or none.")
        if set_count == 4:
            for name, val in [("top", self.top), ("bottom", self.bottom),
                               ("left", self.left), ("right", self.right)]:
                if not (0.3 <= val <= 1.0):
                    raise ValueError(f"{name} margin must be between 0.3 and 1.0 inches")
        return self


class ResumeLayoutOptions(BaseSchema):
    body_font_size_pt: int = 10
    name_font_size_pt: int = 14
    margins_in: ResumeMarginsInches | None = None

    @field_validator("body_font_size_pt")
    @classmethod
    def validate_body_font(cls, v: int) -> int:
        if not (9 <= v <= 12):
            raise ValueError("body_font_size_pt must be between 9 and 12")
        return v

    @field_validator("name_font_size_pt")
    @classmethod
    def validate_name_font(cls, v: int) -> int:
        if not (12 <= v <= 18):
            raise ValueError("name_font_size_pt must be between 12 and 18")
        return v


class RenderResumeRequest(BaseSchema):
    layout: ResumeLayoutOptions | None = None


class RenderedResumeResponse(BaseSchema):
    job_profile_id: int
    template_name: str
    rendered_at: datetime
    layout_json: dict
