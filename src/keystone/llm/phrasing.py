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
from dataclasses import dataclass

from keystone.core.deontic import drifts
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


@dataclass(frozen=True)
class PhrasedSummary:
    """Result of phrasing: the text to display, and whether it fell back.

    `text` is the reworded summary when faithful, or the curated `summary`
    verbatim when the deontic guard detected modal drift. `fell_back` is True in
    the latter case so the UI can label it as the (authoritative) source text.
    """

    text: str
    fell_back: bool


def phrase_summary(
    obligation: Obligation, *, backend: Backend | None = None
) -> PhrasedSummary:
    """Reword `obligation.summary` for readability, guarded against modal drift.

    Reads `obligation.summary` and returns derived text; never mutates the
    obligation or any core data. If the reworded text would strengthen or weaken
    the obligation's modal force relative to the curated source (`deontic.drifts`),
    it falls back to the curated summary — certainly-faithful over probably-
    faithful. `backend` is injectable for tests (the fast gate uses a fake one).
    """
    phrased = complete(
        obligation.summary,
        system=PHRASING_SYSTEM,
        backend=backend or _phrasing_backend(),
    ).strip()
    if drifts(obligation.summary, phrased):
        return PhrasedSummary(text=obligation.summary, fell_back=True)
    return PhrasedSummary(text=phrased, fell_back=False)
