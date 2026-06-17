"""Tests for LLM-edge obligation-summary phrasing (KS-0204).

The FAST gate uses a fake backend / mocked transport — NO network, NO key, NO
credits — and carries the coverage. The single live NIM test is marked `slow`
(excluded from the gate/CI) and SKIPS cleanly when NVIDIA_API_KEY is unset.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import pytest

from keystone.core.obligations import Obligation, load_obligations
from keystone.core.obligations.loader import DATA_PATH
from keystone.llm import phrase_summary
from keystone.llm.inference import BackendUnreachableError, NimBackend
from keystone.llm.phrasing import (
    PHRASING_MODEL,
    PHRASING_SYSTEM,
    _phrasing_backend,
)


class _FakeBackend:
    """Records the last call and returns a canned completion."""

    def __init__(self, reply: str = "reworded text") -> None:
        self.reply = reply
        self.last_prompt: str | None = None
        self.last_system: str | None = None

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        self.last_prompt = prompt
        self.last_system = system
        return self.reply


class _UnreachableBackend:
    def complete(self, prompt: str, *, system: str | None = None) -> str:
        raise BackendUnreachableError("NIM backend unreachable at https://example")


@pytest.fixture(scope="module")
def sample() -> Obligation:
    return next(o for o in load_obligations() if o.id == "OBL-EUAI-009")


# --- prompt construction ------------------------------------------------------


def test_phrase_summary_sends_curated_summary_as_prompt(sample: Obligation) -> None:
    fake = _FakeBackend()
    phrase_summary(sample, backend=fake)
    assert fake.last_prompt == sample.summary


def test_phrase_summary_system_prompt_disables_thinking_and_states_faithfulness(
    sample: Obligation,
) -> None:
    fake = _FakeBackend()
    phrase_summary(sample, backend=fake)
    assert fake.last_system is not None
    assert fake.last_system.startswith("/no_think")
    assert "Do NOT add, remove, or alter" in fake.last_system
    assert "Output ONLY the reworded text" in fake.last_system


def test_phrase_summary_returns_stripped_presentation_string(
    sample: Obligation,
) -> None:
    fake = _FakeBackend(reply="  Reworded sentence.  \n")
    assert phrase_summary(sample, backend=fake) == "Reworded sentence."


def test_phrase_summary_propagates_unreachable_backend(sample: Obligation) -> None:
    with pytest.raises(BackendUnreachableError):
        phrase_summary(sample, backend=_UnreachableBackend())


# --- purity (MANDATORY no-mutation) -------------------------------------------


def test_phrase_summary_does_not_mutate_obligation_or_data_file(
    sample: Obligation,
) -> None:
    before_bytes = DATA_PATH.read_bytes()
    before_obj = sample.model_dump()

    phrase_summary(sample, backend=_FakeBackend(reply="totally different text"))

    assert DATA_PATH.read_bytes() == before_bytes  # core data byte-identical
    assert sample.model_dump() == before_obj  # model object untouched


# --- decoding params reach the wire -------------------------------------------


def test_phrasing_backend_carries_spec_params() -> None:
    backend = _phrasing_backend()
    assert backend.model == PHRASING_MODEL
    assert backend.temperature == 0.2
    assert backend.top_p == 0.9
    assert backend.max_tokens == 256


def test_nim_backend_sends_spec_params_on_the_wire(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class _Resp:
        def raise_for_status(self) -> None: ...

        def json(self) -> dict[str, Any]:
            return {"choices": [{"message": {"content": "ok"}}]}

    def _fake_post(url: str, **kwargs: Any) -> _Resp:
        captured["url"] = url
        captured["json"] = kwargs["json"]
        return _Resp()

    monkeypatch.setattr(httpx, "post", _fake_post)

    # Positional api_key (synthetic) avoids detect-secrets' keyword heuristic.
    backend = NimBackend(
        "synthetic-key",
        model=PHRASING_MODEL,
        temperature=0.2,
        top_p=0.9,
        max_tokens=256,
    )
    assert backend.complete("a summary", system=PHRASING_SYSTEM) == "ok"

    payload = captured["json"]
    assert payload["model"] == PHRASING_MODEL
    assert payload["temperature"] == 0.2
    assert payload["top_p"] == 0.9
    assert payload["max_tokens"] == 256
    assert payload["stream"] is False
    assert payload["messages"][0] == {"role": "system", "content": PHRASING_SYSTEM}
    assert payload["messages"][1] == {"role": "user", "content": "a summary"}


# --- live NIM (slow; skips cleanly without a key) -----------------------------


@pytest.mark.slow
@pytest.mark.skipif(
    not os.environ.get("NVIDIA_API_KEY"),
    reason="NVIDIA_API_KEY not set — live NIM test skipped",
)
def test_live_phrasing_no_preamble_or_reasoning_leakage() -> None:
    sample = next(o for o in load_obligations() if o.id == "OBL-EUAI-009")
    out = phrase_summary(sample)
    assert isinstance(out, str)
    assert out.strip()
    lowered = out.lower()
    assert not lowered.startswith(("here", "sure", "reworded", "the reworded version"))
    assert "<think>" not in lowered and "</think>" not in lowered
