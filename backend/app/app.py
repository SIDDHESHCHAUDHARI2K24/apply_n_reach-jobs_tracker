"""Application entrypoint and FastAPI factory.

This module configures the FastAPI app instance, attaches middleware
such as CORS, and wires feature routers (for example `auth`).
The `core` feature provides infrastructure only and is consumed
via dependencies, not as a public router.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.features.auth.routers import auth_router
from app.features.core.config import settings
from app.features.core.database import get_db
from app.features.user_profile.personal.router import router as profile_router
from app.features.user_profile.education.router import router as education_router
from app.features.user_profile.experience.router import router as experience_router
from app.features.user_profile.projects.router import router as projects_router
from app.features.user_profile.research.router import router as research_router
from app.features.user_profile.certifications.router import router as certifications_router
from app.features.user_profile.skills.router import router as skills_router
from app.features.job_profile.core.router import router as jp_core_router
from app.features.job_profile.personal.router import router as jp_personal_router
from app.features.job_profile.education.router import router as jp_education_router
from app.features.job_profile.experience.router import router as jp_experience_router
from app.features.job_profile.projects.router import router as jp_projects_router
from app.features.job_profile.research.router import router as jp_research_router
from app.features.job_profile.certifications.router import router as jp_certifications_router
from app.features.job_profile.skills.router import router as jp_skills_router
from app.features.job_profile.latex_resume.router import router as jp_latex_resume_router
from app.features.job_tracker.openings_core.router import router as jt_openings_router
from app.features.job_tracker.opening_ingestion.router import router as jt_ingestion_router
from app.features.job_tracker.opening_ingestion.service import startup_stale_run_cleanup
from app.features.job_tracker.opening_resume.router import router as jt_resume_router
from app.features.job_tracker.opening_resume.personal.router import router as jt_resume_personal_router
from app.features.job_tracker.opening_resume.education.router import router as jt_resume_education_router
from app.features.job_tracker.opening_resume.experience.router import router as jt_resume_experience_router
from app.features.job_tracker.opening_resume.projects.router import router as jt_resume_projects_router
from app.features.job_tracker.opening_resume.research.router import router as jt_resume_research_router
from app.features.job_tracker.opening_resume.certifications.router import router as jt_resume_certifications_router
from app.features.job_tracker.opening_resume.skills.router import router as jt_resume_skills_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before serving requests."""
    async with get_db() as conn:
        await startup_stale_run_cleanup(conn)
    yield


def create_app() -> FastAPI:
    """Create and configure the main FastAPI application instance."""
    app = FastAPI(title=settings.project_name, lifespan=lifespan)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Return a standardised error envelope for all HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.status_code},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Return a standardised error envelope for Pydantic 422 validation errors."""
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc.errors()), "code": 422},
        )

    allow_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Simple health check endpoint used for readiness/liveness probes."""
        return {"status": "ok"}

    # Feature routers.
    app.include_router(auth_router)
    app.include_router(profile_router)
    app.include_router(education_router)
    app.include_router(experience_router)
    app.include_router(projects_router)
    app.include_router(research_router)
    app.include_router(certifications_router)
    app.include_router(skills_router)

    # Job profile routers.
    app.include_router(jp_core_router)
    app.include_router(jp_personal_router)
    app.include_router(jp_education_router)
    app.include_router(jp_experience_router)
    app.include_router(jp_projects_router)
    app.include_router(jp_research_router)
    app.include_router(jp_certifications_router)
    app.include_router(jp_skills_router)
    app.include_router(jp_latex_resume_router)

    # Job tracker routers.
    app.include_router(jt_openings_router)
    app.include_router(jt_ingestion_router)
    app.include_router(jt_resume_router)
    app.include_router(jt_resume_personal_router)
    app.include_router(jt_resume_education_router)
    app.include_router(jt_resume_experience_router)
    app.include_router(jt_resume_projects_router)
    app.include_router(jt_resume_research_router)
    app.include_router(jt_resume_certifications_router)
    app.include_router(jt_resume_skills_router)

    return app
