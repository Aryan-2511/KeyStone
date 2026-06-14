"""Hosted NIM backend (build.nvidia.com, OpenAI-compatible chat completions).

Endpoint: POST {base_url}/chat/completions with `Authorization: Bearer <key>`.
The API key comes from NVIDIA_API_KEY and is never logged.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

from .base import BackendUnreachableError, InferenceError

DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"


@dataclass(frozen=True)
class NimBackend:
    """OpenAI-compatible hosted NIM backend."""

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: float = 30.0

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        if not self.api_key:
            raise InferenceError(
                "NVIDIA_API_KEY is not set; cannot use the nim backend"
            )

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages, "temperature": 0.0},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            # Note: no api_key in the message.
            raise BackendUnreachableError(
                f"NIM backend unreachable at {self.base_url}"
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise InferenceError(
                f"NIM backend returned HTTP {exc.response.status_code}"
            ) from exc

        data = response.json()
        return str(data["choices"][0]["message"]["content"])
