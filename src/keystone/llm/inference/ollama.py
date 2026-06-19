"""Local Ollama backend (native chat API).

Endpoint: POST {host}/api/chat with `{"model", "messages", "stream": false}`,
returning `{"message": {"content": ...}}`. No auth; local by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from .base import BackendUnreachableError, InferenceError
from .tools import ToolCallResult, normalize_tool_calls

DEFAULT_HOST = "http://localhost:11434"
# qwen2.5:3b is the Layer-2 backend chosen by the tool-calling spike (MEMORY.md):
# free, local, and more reliable at tool-calling than the hosted NIM model. Keeping
# it the default means the live roundtrip test hits a model that is actually pulled.
DEFAULT_MODEL = "qwen2.5:3b"


@dataclass(frozen=True)
class OllamaBackend:
    """Local Ollama backend."""

    host: str = DEFAULT_HOST
    model: str = DEFAULT_MODEL
    timeout: float = 30.0

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = httpx.post(
                f"{self.host}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise BackendUnreachableError(
                f"Ollama backend unreachable at {self.host} "
                "(is `ollama serve` running?)"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise InferenceError(
                f"Ollama backend returned HTTP {exc.response.status_code}"
            ) from exc

        data = response.json()
        return str(data["message"]["content"])

    def complete_with_tools(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ToolCallResult:
        """Tool-calling completion via `/api/chat` with a `tools` array.

        Ollama returns tool-call `arguments` as a JSON object; the normalizer
        passes that through. Temperature is pinned to 0 for reproducible
        tool selection (the spike ran at temp 0).
        """
        try:
            response = httpx.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": tools,
                    "stream": False,
                    "options": {"temperature": 0},
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            raise BackendUnreachableError(
                f"Ollama backend unreachable at {self.host} "
                "(is `ollama serve` running?)"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise InferenceError(
                f"Ollama backend returned HTTP {exc.response.status_code}"
            ) from exc

        message = response.json().get("message", {})
        content = str(message.get("content") or "") if isinstance(message, dict) else ""
        raw_calls = message.get("tool_calls") if isinstance(message, dict) else None
        return ToolCallResult(
            content=content, tool_calls=normalize_tool_calls(raw_calls)
        )
