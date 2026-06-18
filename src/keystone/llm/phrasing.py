"""LLM-edge obligation-summary phrasing (KS-0204).

This is a SEPARATE, edge-side transform (ADR-0012 §4): it READS an obligation's
curated `summary` — the human-written system of record — and returns DERIVED
presentation text. It MUST NOT write back to any core store; `summary` and the
obligation model are left byte-identical. Inference goes through the one allowed
seam, `keystone.llm.inference` (ADR-0008: only the edge calls an LLM).

The model is a hybrid-reasoning model run in NO-THINK mode for a rewording task;
the system prompt both disables thinking (`/no_think`) and states the
faithfulness contract. Live-on-demand, no caching.
"""

from __future__ import annotations

import os

from keystone.core.obligations import Obligation

from .inference import Backend, NimBackend, complete

# Hybrid-reasoning model, run in no-think mode (see the system prompt).
PHRASING_MODEL = "nvidia/nvidia-nemotron-nano-9b-v2"

# `/no_think` disables reasoning; the rest is the faithfulness contract. The
# phrased text is PRESENTATION ONLY — the model must not add, drop, or alter facts.
PHRASING_SYSTEM = (
    "/no_think\n"
    "Reword the following regulatory obligation summary for readability. Do NOT "
    "add, remove, or alter any fact, article number, regulation name, date, or "
    "obligation. Output ONLY the reworded text — no preamble, no explanation."
)

# Decoding for a faithful rewording: low temperature, capped length (KS-0204 spec).
_TEMPERATURE = 0.2
_TOP_P = 0.9
_MAX_TOKENS = 256


def _phrasing_backend() -> NimBackend:
    """Build the NIM backend pinned to the phrasing model + decoding params.

    Reads `NVIDIA_API_KEY` from the environment (never logged). Independent of
    `KEYSTONE_NIM_MODEL` so phrasing always uses the validated model.
    """
    return NimBackend(
        api_key=os.environ.get("NVIDIA_API_KEY", ""),
        base_url=os.environ.get("KEYSTONE_NIM_BASE_URL", NimBackend.base_url),
        model=PHRASING_MODEL,
        timeout=float(os.environ.get("KEYSTONE_INFERENCE_TIMEOUT", "30")),
        temperature=_TEMPERATURE,
        top_p=_TOP_P,
        max_tokens=_MAX_TOKENS,
    )


def phrase_summary(obligation: Obligation, *, backend: Backend | None = None) -> str:
    """Return a reworded, presentation-only version of `obligation.summary`.

    Reads `obligation.summary` and returns derived text; does not mutate the
    obligation or any core data. `backend` is injectable for tests (the fast gate
    passes a fake backend so it never touches the network).
    """
    return complete(
        obligation.summary,
        system=PHRASING_SYSTEM,
        backend=backend or _phrasing_backend(),
    ).strip()
