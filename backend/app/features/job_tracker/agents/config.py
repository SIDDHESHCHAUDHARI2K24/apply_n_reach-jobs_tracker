"""Agent configuration and LangSmith setup."""
import os
from app.features.core.config import get_settings

# Default model — used when routing through OpenRouter
DEFAULT_MODEL = "google/gemma-3-27b-it:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# OpenAI model (used when OPENAI_API_KEY is set — takes priority over OpenRouter)
OPENAI_MODEL = "gpt-5.4-mini"

LANGSMITH_PROJECT = "ETB_Project"

def configure_langsmith():
    """Ensure LangSmith env vars are set before any LangChain calls.

    Sets both LANGCHAIN_* (legacy) and LANGSMITH_* (v0.6+) names so
    all LangChain / LangSmith versions pick up tracing correctly.
    These are also set directly in .env so they load at import time,
    but this function provides a belt-and-suspenders guarantee.
    """
    settings = get_settings()
    api_key = settings.langchain_api_key
    if not api_key:
        return

    for key_name in ("LANGCHAIN_API_KEY", "LANGSMITH_API_KEY"):
        os.environ[key_name] = api_key

    for tracing_name in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING"):
        os.environ[tracing_name] = "true"

    for project_name in ("LANGCHAIN_PROJECT", "LANGSMITH_PROJECT"):
        os.environ[project_name] = LANGSMITH_PROJECT
