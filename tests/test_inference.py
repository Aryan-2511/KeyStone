"""Tests for the inference switch (KS-0104).

Fast tests use an injected fake backend — no network. The single live test is
marked `slow` and skips if the backend is unreachable.
"""

import pytest

from keystone.llm.inference import (
    BackendUnreachableError,
    InferenceError,
    NimBackend,
    OllamaBackend,
    complete,
    get_backend,
)


class FakeBackend:
    """Records the last call and returns a canned completion."""

    def __init__(self, reply: str = "ok") -> None:
        self.reply = reply
        self.last_prompt: str | None = None
        self.last_system: str | None = None

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        self.last_prompt = prompt
        self.last_system = system
        return self.reply


def test_complete_uses_injected_backend() -> None:
    fake = FakeBackend(reply="hello")
    assert complete("hi", backend=fake) == "hello"
    assert fake.last_prompt == "hi"


def test_complete_passes_system_through() -> None:
    fake = FakeBackend()
    complete("hi", system="be terse", backend=fake)
    assert fake.last_system == "be terse"


def test_default_backend_is_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KEYSTONE_INFERENCE_BACKEND", raising=False)
    assert isinstance(get_backend(), OllamaBackend)


def test_backend_switch_to_nim(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEYSTONE_INFERENCE_BACKEND", "nim")
    monkeypatch.setenv("NVIDIA_API_KEY", "synthetic-key")
    backend = get_backend()
    assert isinstance(backend, NimBackend)


def test_unknown_backend_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEYSTONE_INFERENCE_BACKEND", "bogus")
    with pytest.raises(InferenceError, match="Unknown"):
        get_backend()


def test_nim_without_key_raises_clear_error() -> None:
    # No network: the missing-key guard fires before any HTTP call.
    with pytest.raises(InferenceError, match="NVIDIA_API_KEY"):
        NimBackend(api_key="").complete("hi")


def test_timeout_is_configurable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KEYSTONE_INFERENCE_BACKEND", "ollama")
    monkeypatch.setenv("KEYSTONE_INFERENCE_TIMEOUT", "5")
    backend = get_backend()
    assert isinstance(backend, OllamaBackend)
    assert backend.timeout == 5.0


@pytest.mark.slow
def test_live_backend_roundtrip() -> None:
    """Hits the env-configured live backend; skips if unreachable."""
    try:
        reply = complete("Reply with the single word: pong.")
    except BackendUnreachableError as exc:
        pytest.skip(f"no live backend: {exc}")
    assert isinstance(reply, str)
    assert reply
