"""FINETUNE-SPIKE-01 — a decisive, honestly-scoped QLoRA specialization probe.

The question (from ``docs/paper/finetune_feasibility.md``, verdict VIABLE-but-NARROW):
does task-**specialization** let a small on-prem model make the bounded triage decision
the general 3B failed on (OPT-A-01b held-out: **4/6**)? This package builds the *repo
side* of that probe — the frozen held-out eval, the contamination-safe training dataset,
and the mechanical disjointness guarantee — so the eventual measurement is credible
either way it lands.

**What this is NOT.** Not "a fine-tuned agent brain." The labels come from the transparent
policy (:func:`keystone.agents.triage.route_for`), so a fine-tuned model can at most
*distill* the policy — never "reason better" than it (the policy is the label ceiling).
This is a narrow **capacity/specialization** probe, framed exactly that way.

**The credibility guarantee (the whole point).** The held-out eval is frozen BEFORE any
training data exists; the training data is sampled to be **provably disjoint** from it
(reserved threshold band + mechanical near-duplicate filter, :mod:`.protocol`); a
committed test asserts ZERO contamination. Without that, a fine-tune result measures
memory, not generalization — worthless. See :mod:`.protocol` for the law.

**Data-residency.** Training data is SYNTHETIC (generated from the policy over sampled
abstract signals — no PII), so the training *venue* (Colab) is immaterial; deployment
inference runs on-prem via the same Ollama seam as ``qwen2.5:3b`` today. "Trained on
synthetic data, deployed on-prem" — never "trained on-prem."
"""

from __future__ import annotations

from .protocol import (
    NEAR_DUP_EPS,
    RESERVED_BAND_HIGH,
    RESERVED_BAND_LOW,
    Case,
    contaminates_heldout,
    in_reserved_band,
    to_chat_record,
)

__all__ = [
    "NEAR_DUP_EPS",
    "RESERVED_BAND_HIGH",
    "RESERVED_BAND_LOW",
    "Case",
    "contaminates_heldout",
    "in_reserved_band",
    "to_chat_record",
]
