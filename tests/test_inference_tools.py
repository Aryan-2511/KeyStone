"""Tests for the tool-calling inference seam (KS-0300).

The FAST gate uses mocked HTTP — NO network, NO Ollama running, NO NIM key — and
carries the decisive proof: an Ollama-shaped response (arguments as a dict) and a
NIM-shaped response (arguments as a JSON string) normalize to the SAME
`ToolCallResult`. That backend-parity is the spike's core finding made into a
regression test. The single live tool-call per backend is `slow` and skips
cleanly when the backend is unavailable.

Response fixtures mirror the real shapes the spike observed (MEMORY.md).
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import pytest

from keystone.llm.inference import (
    BackendUnreachableError,
    InferenceError,
    NimBackend,
    OllamaBackend,
    ToolCallNormalizationError,
    ToolCallResult,
    complete_with_tools,
    normalize_tool_calls,
)

# --- captured-shape fixtures (the same logical call, two backend encodings) ---

# Ollama /api/chat: arguments is a JSON OBJECT (dict); tool calls under `message`.
OLLAMA_RESPONSE: dict[str, Any] = {
    "model": "qwen2.5:3b",
    "message": {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "function": {
                    "name": "initiate_transfer",
                    "arguments": {"amount": 500, "recipient": "ACME-123"},
                }
            }
        ],
    },
    "done": True,
}

# NIM /chat/completions: arguments is a JSON STRING; tool calls under choices[0].
NIM_RESPONSE: dict[str, Any] = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "initiate_transfer",
                            "arguments": '{"amount": 500, "recipient": "ACME-123"}',
                        },
                    }
                ],
            }
        }
    ]
}

MESSAGES: list[dict[str, Any]] = [
    {"role": "user", "content": "transfer 500 to ACME-123"}
]
TOOLS: list[dict[str, Any]] = [
    {"type": "function", "function": {"name": "initiate_transfer", "parameters": {}}}
]


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None: ...

    def json(self) -> dict[str, Any]:
        return self._payload


def _patch_post(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    def _fake_post(url: str, **kwargs: Any) -> _FakeResponse:
        return _FakeResponse(payload)

    monkeypatch.setattr(httpx, "post", _fake_post)


# --- the normalizer: dict and string arguments collapse to one shape ----------


def test_normalize_dict_and_string_arguments_are_identical() -> None:
    from_dict = normalize_tool_calls(OLLAMA_RESPONSE["message"]["tool_calls"])
    from_string = normalize_tool_calls(
        NIM_RESPONSE["choices"][0]["message"]["tool_calls"]
    )
    assert from_dict == from_string  # the spike's core finding, unit-level
    assert from_dict[0].name == "initiate_transfer"
    assert from_dict[0].arguments == {"amount": 500, "recipient": "ACME-123"}


def test_normalize_none_means_no_tool_call() -> None:
    assert normalize_tool_calls(None) == []


def test_normalize_dict_arguments_pass_through_unchanged() -> None:
    calls = normalize_tool_calls(
        [{"function": {"name": "lookup_balance", "arguments": {}}}]
    )
    assert calls[0].arguments == {}


def test_normalize_missing_arguments_default_to_empty_dict() -> None:
    # lookup_balance takes no args — Ollama may omit `arguments` entirely.
    calls = normalize_tool_calls([{"function": {"name": "lookup_balance"}}])
    assert calls[0].arguments == {}


@pytest.mark.parametrize(
    ("raw", "match"),
    [
        ("not-a-list", "must be a list"),
        ([{"function": {"name": "f", "arguments": "[1,2]"}}], "must be an object"),
        ([{"no_function": True}], "missing a 'function'"),
        ([{"function": {"arguments": {}}}], "non-empty string"),
        ([{"function": {"name": "f", "arguments": 42}}], "unexpected tool-call"),
        (["not-a-dict"], "must be an object"),
    ],
)
def test_normalize_rejects_malformed_payloads(raw: object, match: str) -> None:
    with pytest.raises(ToolCallNormalizationError, match=match):
        normalize_tool_calls(raw)


# --- per-backend: each backend produces the canonical result ------------------


def test_ollama_backend_normalizes_dict_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_post(monkeypatch, OLLAMA_RESPONSE)
    result = OllamaBackend().complete_with_tools(MESSAGES, TOOLS)
    assert isinstance(result, ToolCallResult)
    assert result.content == ""
    assert result.tool_calls[0].arguments == {"amount": 500, "recipient": "ACME-123"}


def test_nim_backend_normalizes_string_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_post(monkeypatch, NIM_RESPONSE)
    result = NimBackend("synthetic-key").complete_with_tools(MESSAGES, TOOLS)
    assert result.content == ""
    assert result.tool_calls[0].arguments == {"amount": 500, "recipient": "ACME-123"}


def test_backend_parity_ollama_and_nim_yield_identical_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # THE regression test: flipping backend must not change structured results.
    _patch_post(monkeypatch, OLLAMA_RESPONSE)
    ollama_result = OllamaBackend().complete_with_tools(MESSAGES, TOOLS)

    _patch_post(monkeypatch, NIM_RESPONSE)
    nim_result = NimBackend("synthetic-key").complete_with_tools(MESSAGES, TOOLS)

    assert ollama_result == nim_result


# --- text-only and malformed paths --------------------------------------------


def test_text_only_response_has_empty_tool_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    text_only = {"message": {"role": "assistant", "content": "Your balance is $100."}}
    _patch_post(monkeypatch, text_only)
    result = OllamaBackend().complete_with_tools(MESSAGES, TOOLS)
    assert result.tool_calls == []
    assert result.content == "Your balance is $100."


def test_malformed_string_arguments_raise_typed_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    broken = {
        "choices": [
            {
                "message": {
                    "content": None,
                    "tool_calls": [
                        {"function": {"name": "initiate_transfer", "arguments": "{not"}}
                    ],
                }
            }
        ]
    }
    _patch_post(monkeypatch, broken)
    with pytest.raises(ToolCallNormalizationError, match="not valid JSON"):
        NimBackend("synthetic-key").complete_with_tools(MESSAGES, TOOLS)


def test_unreachable_backend_surfaces_cleanly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # This is what lets the live test skip (not error) when Ollama is down.
    def _raise(url: str, **kwargs: Any) -> _FakeResponse:
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "post", _raise)
    with pytest.raises(BackendUnreachableError):
        OllamaBackend().complete_with_tools(MESSAGES, TOOLS)


def test_nim_tool_call_without_key_raises_clear_error() -> None:
    with pytest.raises(InferenceError, match="NVIDIA_API_KEY"):
        NimBackend(api_key="").complete_with_tools(MESSAGES, TOOLS)


# --- the free dispatch function -----------------------------------------------


class _FakeToolBackend:
    def complete_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]
    ) -> ToolCallResult:
        return ToolCallResult(content="ok", tool_calls=[])


class _PlainBackend:
    def complete(self, prompt: str, *, system: str | None = None) -> str:
        return "no tools here"


def test_complete_with_tools_dispatches_to_injected_backend() -> None:
    result = complete_with_tools(MESSAGES, TOOLS, backend=_FakeToolBackend())
    assert result.content == "ok"


def test_complete_with_tools_rejects_non_tool_calling_backend() -> None:
    with pytest.raises(InferenceError, match="does not support tool calling"):
        complete_with_tools(MESSAGES, TOOLS, backend=_PlainBackend())  # type: ignore[arg-type]


# --- live tool-call per backend (slow; skips cleanly when unavailable) ---------

_TOOLS_LIVE: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "lookup_balance",
            "description": "Look up the current account balance.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    }
]
_MESSAGES_LIVE: list[dict[str, Any]] = [
    {"role": "user", "content": "What is my current account balance?"}
]


@pytest.mark.slow
def test_live_ollama_tool_call_normalizes() -> None:
    try:
        result = complete_with_tools(
            _MESSAGES_LIVE, _TOOLS_LIVE, backend=OllamaBackend()
        )
    except BackendUnreachableError as exc:
        pytest.skip(f"Ollama not running: {exc}")
    assert isinstance(result, ToolCallResult)
    for call in result.tool_calls:
        assert isinstance(call.arguments, dict)  # normalized shape holds live


@pytest.mark.slow
@pytest.mark.skipif(
    not os.environ.get("NVIDIA_API_KEY"),
    reason="NVIDIA_API_KEY not set — live NIM tool-call skipped",
)
def test_live_nim_tool_call_normalizes() -> None:
    backend = NimBackend(
        api_key=os.environ["NVIDIA_API_KEY"],
        model="nvidia/nvidia-nemotron-nano-9b-v2",
    )
    result = complete_with_tools(_MESSAGES_LIVE, _TOOLS_LIVE, backend=backend)
    assert isinstance(result, ToolCallResult)
    for call in result.tool_calls:
        assert isinstance(call.arguments, dict)
