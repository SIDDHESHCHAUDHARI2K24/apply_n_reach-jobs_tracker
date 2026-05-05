"""Application configuration and environment settings for the backend.

This module centralizes configuration using `pydantic-settings`. It
reads values from the process environment and the local `.env` file
in the backend directory. Use the `settings` singleton or the
`get_settings()` helper in dependencies instead of instantiating
`Settings` directly.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed configuration model for the application.

    Attributes:
        project_name: Human-friendly name for the service.
        environment: Deployment environment identifier (e.g. local, dev, prod).
        database_url: PostgreSQL connection URL used by the async driver.
        log_level: Application log level (e.g. INFO, DEBUG).
    """

    project_name: str = "FastAPI Backend Boilerplate"
    environment: str = "local"
    database_url: str
    log_level: str = "INFO"
    openrouter_api_key: str | None = None
    openai_api_key: str | None = None
    langchain_api_key: str | None = None
    apify_api_token: str | None = None
    cors_allow_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    session_cookie_secure: bool = False
    session_cookie_samesite: Literal["lax", "strict", "none"] = "lax"

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins(self) -> list[str]:
        """Return configured CORS origins parsed from comma-delimited env input."""
        raw = self.cors_allow_origins.strip()
        if not raw:
            return []
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of `Settings` loaded from the environment."""
    return Settings()


settings = get_settings()

