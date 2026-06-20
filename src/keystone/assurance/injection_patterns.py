"""Deterministic data-field injection detection (KS-0302) — typed, no LLM.

The security-critical logic of the NeMo Guardrails input rail lives here so it is
fully type-checked and unit-testable without constructing the rail. The rail's
`actions.py` is a thin shim that calls `is_data_field_injection`.

It flags content that reads as embedded *instructions*: an instruction-OVERRIDE
phrase (the Garak latent-injection payloads — "ignore the above directions",
"just print X", "system:") or an imperative settlement DIRECTIVE (the canonical
memo exploit — "pre-approved", "initiate a transfer", "send ... to account"). A
normal payment memo contains neither, so a legitimate transfer — authorized by the
user's command, not by data-field text — is not over-blocked.
"""

from __future__ import annotations

import re

_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = (
    # instruction-override phrasing (covers Garak's latent-injection payloads)
    re.compile(
        r"\b(?:ignore|disregard|forget|do not (?:follow|listen))\b[^.]*?"
        r"\b(?:instruction|direction|above|prior|previous|rule|prompt|therein)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bjust\s+(?:print|say|output|return|respond|translate)\b", re.IGNORECASE
    ),
    re.compile(r"\btranslate\s+this\s+(?:sentence|text)\s+as\b", re.IGNORECASE),
    # echo / repeat directive ("please repeat the following sentence: X")
    re.compile(
        r"\brepeat\b[^.]*?\b(?:following|sentence|this|after|verbatim)", re.IGNORECASE
    ),
    re.compile(r"\b(?:print|say|output|write)\b[^.]*?[\"']", re.IGNORECASE),
    re.compile(r"\bas\s+instructed\b", re.IGNORECASE),
    # an injected fake conversation turn (User:/Assistant:/System:)
    re.compile(r"(?:^|\n|\s)(?:user|assistant|system)\s*:", re.IGNORECASE),
    # imperative settlement directive (the canonical memo exploit)
    re.compile(r"\bpre-?approved\b", re.IGNORECASE),
    re.compile(r"\binitiate\b[^.]*\btransfer\b", re.IGNORECASE),
    re.compile(r"\btransfer\b[^.]*\bto\s+account\b", re.IGNORECASE),
    re.compile(r"\b(?:send|wire|pay)\b[^.]*\bto\s+account\b", re.IGNORECASE),
)


def is_data_field_injection(text: str) -> bool:
    """True if `text` reads as embedded instructions (deterministic, no LLM)."""
    return any(pattern.search(text) for pattern in _INJECTION_PATTERNS)
