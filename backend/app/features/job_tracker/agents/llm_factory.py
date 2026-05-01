"""LLM factory for agent nodes."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from app.features.core.config import get_settings
from app.features.job_tracker.agents.config import DEFAULT_MODEL, OPENROUTER_BASE_URL, OPENAI_MODEL

if TYPE_CHECKING:
    from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def get_chat_llm(
    model: str | None = None,
    temperature: float = 0,
    **kwargs,
) -> "ChatOpenAI":
    """Create a ChatOpenAI instance.

    Priority:
      1. OpenAI directly (if OPENAI_API_KEY is set) — uses gpt-4o-mini
      2. OpenRouter (if OPENROUTER_API_KEY is set) — uses the provided/default model

    Raises:
        RuntimeError: If neither API key is configured.
        ImportError: If langchain_openai is not installed.
    """
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        raise ImportError(
            "langchain_openai is required for LLM calls. Run: uv sync"
        ) from e

    settings = get_settings()

    # Prefer OpenAI when key is available
    if settings.openai_api_key:
        resolved_model = OPENAI_MODEL  # always gpt-4o-mini regardless of caller arg
        return ChatOpenAI(
            model=resolved_model,
            api_key=settings.openai_api_key,
            temperature=temperature,
            **kwargs,
        )

    # Fall back to OpenRouter
    if not settings.openrouter_api_key:
        raise RuntimeError(
            "No LLM API key configured. Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env"
        )
    resolved_model = model or DEFAULT_MODEL
    return ChatOpenAI(
        model=resolved_model,
        api_key=settings.openrouter_api_key,
        base_url=OPENROUTER_BASE_URL,
        temperature=temperature,
        **kwargs,
    )


def _merge_system_into_human(messages: list) -> list:
    """Fold SystemMessage into the first HumanMessage for models that don't support system prompts.

    Gemma via Google AI Studio rejects SystemMessage ('developer instruction not enabled').
    Merges as: "<system_content>\\n\\n<human_content>"
    """
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
    except ImportError:
        return messages

    result = []
    pending_system = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            pending_system.append(msg.content)
        elif isinstance(msg, HumanMessage) and pending_system:
            merged = "\n\n".join(pending_system) + "\n\n" + msg.content
            result.append(HumanMessage(content=merged))
            pending_system = []
        else:
            if pending_system:
                # Flush orphaned system content as a human message
                result.append(HumanMessage(content="\n\n".join(pending_system)))
                pending_system = []
            result.append(msg)
    return result


async def ainvoke_with_retry(llm, messages, *, max_retries: int = 5, base_delay: float = 15.0):
    """Invoke an LLM with exponential backoff on 429 rate-limit errors.

    Also handles Gemma's lack of system message support by folding SystemMessage
    content into the first HumanMessage on 400 'developer instruction' errors.

    Args:
        llm: LangChain LLM instance.
        messages: List of messages to send.
        max_retries: Maximum number of retry attempts.
        base_delay: Base delay in seconds (doubles each attempt).

    Returns:
        LLM response.
    """
    # Try with original messages first; fall back to merged on 400 system-message errors
    current_messages = messages
    delay = base_delay
    for attempt in range(max_retries + 1):
        try:
            return await llm.ainvoke(current_messages)
        except Exception as e:
            err_str = str(e)
            is_rate_limit = "429" in err_str
            is_system_unsupported = "400" in err_str and "developer instruction" in err_str.lower()

            if is_system_unsupported:
                # Gemma doesn't support system messages — merge and retry immediately
                logger.info("Model doesn't support system messages; merging into human turn")
                current_messages = _merge_system_into_human(messages)
                continue  # retry immediately with merged messages

            if is_rate_limit and attempt < max_retries:
                logger.warning(
                    "Rate limit hit (attempt %d/%d), retrying in %.0fs...",
                    attempt + 1, max_retries, delay,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, 120.0)
            else:
                raise
