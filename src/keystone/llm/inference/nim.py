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
    """OpenAI-compatible hosted NIM backend.

    Sampling params live on the instance (not the `complete` signature) so the
    backend stays drop-in for the `Backend` protocol while callers that need
    specific decoding — e.g. KS-0204's faithful rewording — construct a backend
    pinned to a model and `temperature`/`top_p`/`max_tokens`.
    """

    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: float = 30.0
    temperature: float = 0.0
    top_p: float = 1.0
    max_tokens: int | None = None

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        if not self.api_key:
            raise InferenceError(
                "NVIDIA_API_KEY is not set; cannot use the nim backend"
            )

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict[str, object] = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stream": False,
        }
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens

        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
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
