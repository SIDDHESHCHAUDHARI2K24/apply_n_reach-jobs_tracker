"""Tests for the LLM factory module."""
import pytest
from unittest.mock import patch

from app.features.job_tracker.agents.llm_factory import get_chat_llm
from app.features.job_tracker.agents.config import DEFAULT_MODEL, OPENROUTER_BASE_URL


def test_get_chat_llm_no_api_key():
    """Should raise RuntimeError when openrouter_api_key is not configured."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openrouter_api_key = None
        with pytest.raises(RuntimeError, match="openrouter_api_key not configured"):
            get_chat_llm()


def test_get_chat_llm_returns_chat_openai():
    """Should return a ChatOpenAI instance with correct config."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openrouter_api_key = "test-key-123"
        llm = get_chat_llm()

        assert llm.model_name == DEFAULT_MODEL
        assert str(llm.openai_api_base) == OPENROUTER_BASE_URL
        assert llm.temperature == 0


def test_get_chat_llm_custom_params():
    """Should accept custom model and temperature."""
    with patch("app.features.job_tracker.agents.llm_factory.get_settings") as mock_settings:
        mock_settings.return_value.openrouter_api_key = "test-key-123"
        llm = get_chat_llm(model="gpt-4o", temperature=0.7)

        assert llm.model_name == "gpt-4o"
        assert llm.temperature == 0.7
