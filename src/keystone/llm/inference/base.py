"""Backend protocol and errors for the inference switch (LLM edge).

This is the ONLY place in Keystone allowed to call an LLM. Backends are selected
by config (env var); see `__init__.py`. No secrets are ever logged.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class InferenceError(Exception):
    """Base error for the inference layer."""


class BackendUnreachableError(InferenceError):
    """Raised when a backend cannot be reached (connection/timeout)."""


@runtime_checkable
class Backend(Protocol):
    """A text-completion backend."""

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        """Return a completion for `prompt`, optionally steered by `system`."""
        ...
