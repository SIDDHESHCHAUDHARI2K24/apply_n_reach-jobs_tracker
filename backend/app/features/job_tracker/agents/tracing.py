"""LangSmith tracing utilities."""
from __future__ import annotations
from typing import Any
from langchain_core.runnables import Runnable, RunnableConfig


def wrap_runnable(
    runnable: Runnable,
    *,
    name: str,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Runnable:
    """Wrap a runnable with LangSmith tracing metadata.

    Args:
        runnable: The LangChain runnable to wrap.
        name: Display name in LangSmith traces.
        tags: Optional tags for filtering.
        metadata: Optional metadata dict.

    Returns:
        The runnable with tracing config applied.
    """
    config = RunnableConfig(
        run_name=name,
        tags=tags or [],
        metadata=metadata or {},
    )
    return runnable.with_config(config)
