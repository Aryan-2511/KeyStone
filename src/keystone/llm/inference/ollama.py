"""Local Ollama backend (native chat API).

Endpoint: POST {host}/api/chat with `{"model", "messages", "stream": false}`,
returning `{"message": {"content": ...}}`. No auth; local by default.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from .base import BackendUnreachableError, InferenceError

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"


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
