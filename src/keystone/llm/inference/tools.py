"""Tool-calling result model + cross-backend normalization (KS-0301, LLM edge).

The plain `complete()` path cannot tool-call (it sends no tools). This adds the
canonical typed shape every tool-calling caller sees, regardless of backend, so
flipping `KEYSTONE_INFERENCE_BACKEND` yields identical structured results.

The one cross-backend wrinkle the spike found (MEMORY.md): tool-call arguments
come back as a JSON **object** from Ollama (`/api/chat`) but as a JSON **string**
from NIM (OpenAI-compatible `/chat/completions`). `normalize_tool_calls`
collapses both into one shape — `arguments` is ALWAYS a `dict`. A model that
answers in text instead of calling a tool yields an EMPTY `tool_calls` list (a
valid outcome, not an error); a genuinely malformed arguments payload raises a
clear, typed error.

Deterministic shaping only — no network, no model call lives here.
"""

from __future__ import annotations

import json
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict

from .base import InferenceError


class ToolCallNormalizationError(InferenceError):
    """Raised when a backend's tool-call payload cannot be normalized."""


class ToolCall(BaseModel):
    """One normalized tool call: a function name and its argument object.

    `arguments` is ALWAYS a dict — the JSON-string form (NIM) is parsed and the
    dict form (Ollama) passes through — so callers never branch on backend.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    arguments: dict[str, Any]


class ToolCallResult(BaseModel):
    """The canonical result of a tool-calling completion.

    `content` is any assistant text (empty string when the model only emitted
    tool calls); `tool_calls` is empty when the model answered in text instead.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    content: str
    tool_calls: list[ToolCall]


@runtime_checkable
class ToolCallingBackend(Protocol):
    """A backend that can return normalized tool calls for a tools array."""

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ToolCallResult:
        """Send `messages` + `tools` and return a normalized `ToolCallResult`."""
        ...


def _coerce_arguments(raw: object) -> dict[str, Any]:
    """Coerce a tool call's `arguments` (dict OR JSON string) into a dict."""
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return {str(key): value for key, value in raw.items()}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ToolCallNormalizationError(
                f"tool-call arguments are not valid JSON: {raw!r}"
            ) from exc
        if not isinstance(parsed, dict):
            raise ToolCallNormalizationError(
                "tool-call arguments JSON must be an object, "
                f"got {type(parsed).__name__}"
            )
        return {str(key): value for key, value in parsed.items()}
    raise ToolCallNormalizationError(
        f"unexpected tool-call arguments type: {type(raw).__name__}"
    )


def normalize_tool_calls(raw_tool_calls: object) -> list[ToolCall]:
    """Normalize a backend's raw `tool_calls` array into typed `ToolCall`s.

    Accepts the Ollama and NIM/OpenAI shapes alike (both nest
    `{"function": {"name", "arguments"}}`); `arguments` is coerced to a dict. A
    missing/None array means the model called no tool → empty list.
    """
    if raw_tool_calls is None:
        return []
    if not isinstance(raw_tool_calls, list):
        raise ToolCallNormalizationError(
            f"tool_calls must be a list, got {type(raw_tool_calls).__name__}"
        )

    calls: list[ToolCall] = []
    for item in raw_tool_calls:
        if not isinstance(item, dict):
            raise ToolCallNormalizationError(
                f"each tool call must be an object, got {type(item).__name__}"
            )
        function = item.get("function")
        if not isinstance(function, dict):
            raise ToolCallNormalizationError("tool call is missing a 'function' object")
        name = function.get("name")
        if not isinstance(name, str) or not name:
            raise ToolCallNormalizationError(
                "tool call 'function.name' must be a non-empty string"
            )
        calls.append(
            ToolCall(name=name, arguments=_coerce_arguments(function.get("arguments")))
        )
    return calls
