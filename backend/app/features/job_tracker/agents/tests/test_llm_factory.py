"""Tests for the LLM factory module."""
import pytest
from unittest.mock import patch

from app.features.job_tracker.agents.llm_factory import get_chat_llm
from app.features.job_tracker.agents.config import DEFAULT_MODEL, OPENAI_MODEL, OPENROUTER_BASE_URL


def test_get_chat_llm_no_api_key():
    """Should raise RuntimeError when neither OpenAI nor OpenRouter key is configured."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openai_api_key = None
        mock_settings.return_value.openrouter_api_key = None
        with pytest.raises(RuntimeError, match="No LLM API key configured"):
            get_chat_llm()


def test_get_chat_llm_openai_takes_priority():
    """When OPENAI_API_KEY is set, should use OpenAI model regardless of OpenRouter key."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openai_api_key = "sk-test-openai"
        mock_settings.return_value.openrouter_api_key = "test-or-key"
        llm = get_chat_llm()

        assert llm.model_name == OPENAI_MODEL


def test_get_chat_llm_openrouter_fallback():
    """When only OPENROUTER_API_KEY is set, should use OpenRouter with DEFAULT_MODEL."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openai_api_key = None
        mock_settings.return_value.openrouter_api_key = "test-key-123"
        llm = get_chat_llm()

        assert llm.model_name == DEFAULT_MODEL
        assert str(llm.openai_api_base) == OPENROUTER_BASE_URL
        assert llm.temperature == 0


def test_get_chat_llm_custom_model_via_openrouter():
    """Custom model parameter is respected when routing through OpenRouter."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openai_api_key = None
        mock_settings.return_value.openrouter_api_key = "test-key-123"
        llm = get_chat_llm(model="gpt-4o", temperature=0.7)

        assert llm.model_name == "gpt-4o"
        assert llm.temperature == 0.7
