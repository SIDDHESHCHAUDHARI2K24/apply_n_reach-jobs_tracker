"""Barrel module that imports all user_profile sub-feature model modules."""

from app.features.user_profile.personal import models as personal_models
from app.features.user_profile.education import models as education_models
from app.features.user_profile.experience import models as experience_models
from app.features.user_profile.projects import models as projects_models
from app.features.user_profile.research import models as research_models
from app.features.user_profile.skills import models as skills_models
from app.features.user_profile.certifications import models as certifications_models

__all__ = [
    "personal_models",
    "education_models",
    "experience_models",
    "projects_models",
    "research_models",
    "skills_models",
    "certifications_models",
]
