"""
llm.py
-------
Configurable LLM provider abstraction.

All nodes import `chat()` from this module instead of calling
the Anthropic SDK directly. Switching providers requires only
a change to the LLM_PROVIDER variable in your .env file.

Supported providers:
  anthropic  — Claude via Anthropic API (best quality, paid)
  groq       — LLaMA / Mixtral via Groq API (free tier, very fast)
  ollama     — Local models via Ollama (free, no internet needed)

.env variables:
  LLM_PROVIDER=groq              # anthropic | groq | ollama
  LLM_MODEL=llama-3.3-70b-versatile  # optional override
  ANTHROPIC_API_KEY=...          # required if provider=anthropic
  GROQ_API_KEY=...               # required if provider=groq
  OLLAMA_BASE_URL=http://localhost:11434  # optional, ollama only

Usage in any node:
  from llm import chat

  response = chat(
      system="You are a...",
      user="Please do...",
      max_tokens=1024,
  )
  # response is always a plain string
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Provider + model defaults
# ---------------------------------------------------------------------------

PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").lower().strip()

_DEFAULT_MODELS = {
    "anthropic": "claude-3-5-sonnet-20241022",
    "groq":      "llama-3.3-70b-versatile",
    "ollama":    "llama3.2",
}

MODEL = os.environ.get("LLM_MODEL") or _DEFAULT_MODELS.get(PROVIDER, "llama3.2")

# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _chat_anthropic(system: str, user: str, max_tokens: int) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return response.content[0].text.strip()


def _chat_groq(system: str, user: str, max_tokens: int) -> str:
    from groq import Groq
    client = Groq()
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response.choices[0].message.content.strip()


def _chat_ollama(system: str, user: str, max_tokens: int) -> str:
    import ollama
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    client = ollama.Client(host=base_url)
    response = client.chat(
        model=MODEL,
        options={"num_predict": max_tokens},
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response["message"]["content"].strip()


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_PROVIDERS = {
    "anthropic": _chat_anthropic,
    "groq":      _chat_groq,
    "ollama":    _chat_ollama,
}


# ---------------------------------------------------------------------------
# Public interface — the only function nodes need
# ---------------------------------------------------------------------------

def chat(system: str, user: str, max_tokens: int = 1024) -> str:
    """
    Send a system + user prompt to the configured LLM provider.

    Args:
        system:     System prompt string.
        user:       User message string.
        max_tokens: Maximum tokens in the response.

    Returns:
        The model's response as a plain string.

    Raises:
        ValueError: If LLM_PROVIDER is set to an unsupported value.
        Exception:  Any API or network error from the provider.
    """
    fn = _PROVIDERS.get(PROVIDER)
    if fn is None:
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{PROVIDER}'. "
            f"Choose from: {', '.join(_PROVIDERS)}"
        )
    return fn(system=system, user=user, max_tokens=max_tokens)


def current_provider_info() -> str:
    """Returns a human-readable string describing the active provider and model."""
    return f"{PROVIDER} / {MODEL}"
