"""The contamination protocol — the law of FINETUNE-SPIKE-01 (finetune_feasibility.md Q3).

Everything that makes the spike *credible* lives here: the reserved threshold band, the
near-duplicate metric, and the single ``contaminates_heldout`` predicate the disjointness
assertion is built on. If a training row satisfies this predicate against the frozen
held-out set, the dataset is contaminated and the result is worthless — the generator must
be fixed, never this predicate.

The task is low-dimensional (a float + two categoricals), so disjointness is **provable by
construction** and **checkable mechanically** — a strength over text fine-tuning, where
contamination is fuzzy. State it that way in the paper.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from keystone.agents.triage import (
    TRIAGE_SYSTEM,
    FindingSeverity,
    Route,
    SeamClassification,
    TriageSignals,
    build_live_prompt,
)

# --------------------------------------------------------------------------- #
# The reserved threshold band (finetune_feasibility.md Q3, Part 1).            #
# route_for's only learnable continuous boundary is the 0.10 action floor. To  #
# test that the model LEARNED the threshold (not memorized training rates), the #
# open band bracketing 0.10 is reserved TEST-ONLY: training never samples a     #
# failure_rate strictly inside it. A memorizer cannot reach an in-band point it #
# never saw; a rule-applier can. This is the axis the general 3B failed on.     #
# --------------------------------------------------------------------------- #
RESERVED_BAND_LOW = 0.05
RESERVED_BAND_HIGH = 0.20

# Two rows with the SAME seam AND severity whose rates are within this distance are
# "near-duplicates" — close enough that including one in training would leak the other.
# Protects held-out points that sit OUTSIDE the band (the reserved exact values, e.g.
# 0.25 / 0.30 / 0.45 from the OPT-A-01b anti-parrot set).
NEAR_DUP_EPS = 0.03


@dataclass(frozen=True, slots=True)
class Case:
    """One labeled example: the observed signals + the policy's route + provenance.

    ``route`` is ALWAYS ``route_for(signals)`` — the frozen policy is the sole labeler
    (a test pins this). ``name`` is a human tag; ``in_band`` records whether the rate is
    inside the reserved threshold band (true only for held-out cases).
    """

    signals: TriageSignals
    route: Route
    name: str
    in_band: bool


def in_reserved_band(rate: float) -> bool:
    """True if ``rate`` is strictly inside the reserved (test-only) threshold band."""
    return RESERVED_BAND_LOW < rate < RESERVED_BAND_HIGH


def _near_any_heldout(signals: TriageSignals, heldout: Iterable[Case]) -> bool:
    """True if ``signals`` is a near-duplicate of any held-out case (same cell, |Δrate|<ε)."""
    return any(
        h.signals.seam_result is signals.seam_result
        and h.signals.severity is signals.severity
        and abs(h.signals.failure_rate - signals.failure_rate) < NEAR_DUP_EPS
        for h in heldout
    )


def contaminates_heldout(signals: TriageSignals, heldout: Iterable[Case]) -> bool:
    """THE disjointness predicate: would a training row on ``signals`` leak the held-out set?

    Contamination iff the rate is inside the reserved band OR the row is a near-duplicate
    (same seam ∧ severity ∧ |Δrate| < :data:`NEAR_DUP_EPS`) of any held-out case. The
    build-time assertion requires this to be ``False`` for EVERY training row. Fix the
    generator if it ever returns ``True`` — never loosen this predicate.
    """
    heldout = list(heldout)
    return in_reserved_band(signals.failure_rate) or _near_any_heldout(signals, heldout)


# --------------------------------------------------------------------------- #
# Serialization: JSONL round-trips for the eval harness and the disjointness   #
# test, plus the chat-format record the Colab QLoRA trainer consumes.          #
# --------------------------------------------------------------------------- #


def case_to_json(case: Case) -> dict[str, object]:
    """A structured, self-describing JSON row (signals + label + provenance)."""
    return {
        "name": case.name,
        "failure_rate": case.signals.failure_rate,
        "seam_result": case.signals.seam_result.value,
        "severity": case.signals.severity.value,
        "route": case.route.value,
        "in_band": case.in_band,
    }


def case_from_json(row: dict[str, object]) -> Case:
    """Rebuild a :class:`Case` from a structured JSON row (inverse of :func:`case_to_json`)."""
    signals = TriageSignals(
        failure_rate=float(row["failure_rate"]),  # type: ignore[arg-type]
        seam_result=SeamClassification(str(row["seam_result"])),
        severity=FindingSeverity(str(row["severity"])),
    )
    return Case(
        signals=signals,
        route=Route(str(row["route"])),
        name=str(row["name"]),
        in_band=bool(row["in_band"]),
    )


def to_chat_record(case: Case) -> dict[str, object]:
    """The QLoRA training record: the EXACT prompt the live eval uses → the route target.

    System + user are byte-for-byte what :func:`keystone.agents.triage.live_triage` sends
    (``TRIAGE_SYSTEM`` + :func:`build_live_prompt`), so the fine-tuned model is trained on
    the same framing it is evaluated on. The assistant target is the route in the parseable
    ``ROUTE: <route>`` format (:func:`keystone.agents.triage.parse_llm_choice` accepts it) —
    the DECISION is the distillation signal; the free-text WHY is deliberately omitted so we
    are not teaching the rule-text to the test.
    """
    user = build_live_prompt(case.signals, tuple(Route))
    return {
        "signals": {
            "failure_rate": case.signals.failure_rate,
            "seam_result": case.signals.seam_result.value,
            "severity": case.signals.severity.value,
        },
        "route": case.route.value,
        "messages": [
            {"role": "system", "content": TRIAGE_SYSTEM},
            {"role": "user", "content": user},
            {"role": "assistant", "content": f"ROUTE: {case.route.value}"},
        ],
    }


def write_cases_jsonl(path: Path, cases: Iterable[Case]) -> None:
    """Write structured eval cases as JSONL (one :func:`case_to_json` per line)."""
    lines = [json.dumps(case_to_json(c), sort_keys=True) for c in cases]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_cases_jsonl(path: Path) -> list[Case]:
    """Read structured eval cases from JSONL (inverse of :func:`write_cases_jsonl`)."""
    return [case_from_json(json.loads(line)) for line in _nonempty_lines(path)]


def write_chat_jsonl(path: Path, cases: Iterable[Case]) -> None:
    """Write training records as chat-format JSONL (one :func:`to_chat_record` per line)."""
    lines = [json.dumps(to_chat_record(c), sort_keys=True) for c in cases]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _nonempty_lines(path: Path) -> Iterator[str]:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            yield line
