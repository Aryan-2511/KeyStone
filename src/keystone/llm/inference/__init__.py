"""Inference switch (LLM edge).

`complete()` is the single entry point. The backend is selected on one code path
by the `KEYSTONE_INFERENCE_BACKEND` env var (`nim` | `ollama`, default `ollama`);
a fake backend can be injected for tests so the fast gate never touches a network.

Env config (all optional except NVIDIA_API_KEY for nim):
- KEYSTONE_INFERENCE_BACKEND   nim | ollama         (default: ollama)
- KEYSTONE_INFERENCE_TIMEOUT   seconds              (default: 30)
- NVIDIA_API_KEY               nim auth (never logged)
- KEYSTONE_NIM_BASE_URL, KEYSTONE_NIM_MODEL
- KEYSTONE_OLLAMA_HOST, KEYSTONE_OLLAMA_MODEL
"""

from __future__ import annotations

import os
from typing import Any

from .base import Backend, BackendUnreachableError, InferenceError
from .nim import NimBackend
from .ollama import OllamaBackend
from .tools import (
    ToolCall,
    ToolCallingBackend,
    ToolCallNormalizationError,
    ToolCallResult,
    normalize_tool_calls,
)

__all__ = [
    "Backend",
    "BackendUnreachableError",
    "InferenceError",
    "NimBackend",
    "OllamaBackend",
    "ToolCall",
    "ToolCallNormalizationError",
    "ToolCallResult",
    "ToolCallingBackend",
    "complete",
    "complete_with_tools",
    "get_backend",
    "normalize_tool_calls",
]

DEFAULT_BACKEND = "ollama"


def _timeout() -> float:
    return float(os.environ.get("KEYSTONE_INFERENCE_TIMEOUT", "30"))


def get_backend() -> Backend:
    """Build the configured backend from the environment (no network I/O)."""
    name = os.environ.get("KEYSTONE_INFERENCE_BACKEND", DEFAULT_BACKEND).strip().lower()
    timeout = _timeout()

    if name == "ollama":
        return OllamaBackend(
            host=os.environ.get("KEYSTONE_OLLAMA_HOST", OllamaBackend.host),
            model=os.environ.get("KEYSTONE_OLLAMA_MODEL", OllamaBackend.model),
            timeout=timeout,
        )
    if name == "nim":
        return NimBackend(
            api_key=os.environ.get("NVIDIA_API_KEY", ""),
            base_url=os.environ.get("KEYSTONE_NIM_BASE_URL", NimBackend.base_url),
            model=os.environ.get("KEYSTONE_NIM_MODEL", NimBackend.model),
            timeout=timeout,
        )
    raise InferenceError(
        f"Unknown KEYSTONE_INFERENCE_BACKEND {name!r}; expected 'nim' or 'ollama'"
    )


def complete(
    prompt: str, *, system: str | None = None, backend: Backend | None = None
) -> str:
    """Complete `prompt` using `backend` (or the env-configured one)."""
    return (backend or get_backend()).complete(prompt, system=system)


def complete_with_tools(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]],
    *,
    backend: ToolCallingBackend | None = None,
) -> ToolCallResult:
    """Tool-calling completion on `backend` (or the env-configured one).

    Sends the `tools` array to whichever backend is active and returns a
    normalized `ToolCallResult` — `arguments` are always a dict and an empty
    `tool_calls` list means the model answered in text. Raises `InferenceError`
    if the active backend does not support tool calling.
    """
    active = backend or get_backend()
    if not isinstance(active, ToolCallingBackend):
        raise InferenceError(
            f"backend {type(active).__name__} does not support tool calling"
        )
    return active.complete_with_tools(messages, tools)
