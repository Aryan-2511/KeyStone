"""Deterministic construction of the frozen held-out eval + the training dataset.

Both are built from the frozen policy (:func:`keystone.agents.triage.route_for`) with **no
RNG** — the same inputs always produce the same rows, so the committed artifacts are
reproducible and auditable (the repo's determinism ethos). The two builders enforce the
ordering the credibility depends on:

1. :func:`build_heldout` — the TEST set, frozen and committed FIRST (before any training
   data exists). Concentrated in the reserved threshold band (the axis general 3B failed),
   plus the OPT-A-01b anti-parrot cases that live outside it.
2. :func:`build_training` — sampled to be **provably disjoint** from a given held-out set:
   failure_rate only from ``[0, 0.05] ∪ [0.20, 1.0]`` (never the reserved band), every row
   checked against :func:`keystone.finetune.protocol.contaminates_heldout`, then balanced
   across the three routes so accuracy is not inflated by a majority class.
"""

from __future__ import annotations

from keystone.agents.triage import (
    FindingSeverity,
    Route,
    SeamClassification,
    TriageSignals,
    route_for,
)

from .protocol import Case, contaminates_heldout, in_reserved_band

# Fixed iteration order (determinism): the categorical grid, smallest structure first.
_SEAMS: tuple[SeamClassification, ...] = (
    SeamClassification.CLEAN,
    SeamClassification.BOUNDARY,
    SeamClassification.OPEN,
)
_SEVERITIES: tuple[FindingSeverity, ...] = (
    FindingSeverity.LOW,
    FindingSeverity.MEDIUM,
    FindingSeverity.HIGH,
)


def _case(
    rate: float, seam: SeamClassification, sev: FindingSeverity, name: str
) -> Case:
    """Build a policy-labeled case (route is ALWAYS route_for — the sole labeler)."""
    signals = TriageSignals(failure_rate=rate, seam_result=seam, severity=sev)
    return Case(
        signals=signals,
        route=route_for(signals),
        name=name,
        in_band=in_reserved_band(rate),
    )


# --------------------------------------------------------------------------- #
# 1. The frozen held-out eval (committed FIRST).                              #
# --------------------------------------------------------------------------- #

# Rates strictly inside the reserved band, bracketing the 0.10 floor on both sides. A model
# that memorized out-of-band training rates cannot classify these; only threshold-learning
# (and correct override/seam handling) gets them right.
_BAND_SWEEP_RATES: tuple[float, ...] = (0.06, 0.08, 0.12, 0.15, 0.18)

# The three OPT-A-01b anti-parrot cases that sit OUTSIDE the band (triage_llm_eval.py:104-153):
# reserved exact values, protected by the near-duplicate filter instead of band exclusion.
_ANTIPARROT_OUT_OF_BAND: tuple[
    tuple[float, SeamClassification, FindingSeverity, str], ...
] = (
    (
        0.25,
        SeamClassification.CLEAN,
        FindingSeverity.LOW,
        "clean LOW above floor -> remediate",
    ),
    (
        0.30,
        SeamClassification.BOUNDARY,
        FindingSeverity.LOW,
        "boundary LOW unshown -> accept",
    ),
    (
        0.45,
        SeamClassification.OPEN,
        FindingSeverity.HIGH,
        "open HIGH mid-rate -> escalate",
    ),
)


def build_heldout() -> list[Case]:
    """The frozen held-out eval: a band sweep across every cell + the out-of-band anti-parrots.

    ~48 cases, each labeled by ``route_for``. The band sweep (5 rates × 9 seam/severity cells)
    exercises the threshold, the HIGH override, and the seam map at rates the training set
    never contains; the three anti-parrot cases add out-of-band generalization. Deterministic
    and stable — this is the immutable test set; nothing downstream may see it.
    """
    cases: list[Case] = []
    for seam in _SEAMS:
        for sev in _SEVERITIES:
            for rate in _BAND_SWEEP_RATES:
                cases.append(
                    _case(
                        rate, seam, sev, f"band {seam.value}/{sev.value} @ {rate:.2f}"
                    )
                )
    for rate, seam, sev, name in _ANTIPARROT_OUT_OF_BAND:
        cases.append(_case(rate, seam, sev, name))
    return cases


# --------------------------------------------------------------------------- #
# 2. The provably-disjoint, route-balanced training set.                      #
# --------------------------------------------------------------------------- #


# Dense, deterministic coverage of the ALLOWED (never-reserved) regions of the rate axis.
# Fine stepping gives genuine continuous diversity, not just grid corners.
def _training_rates() -> tuple[float, ...]:
    low = tuple(round(i * 0.005, 3) for i in range(11))  # 0.000 .. 0.050 (incl. edge)
    high = tuple(
        round(0.20 + i * 0.01, 3) for i in range(81)
    )  # 0.200 .. 1.000 (incl. edge)
    return low + high


def _sort_key(case: Case) -> tuple[str, str, float]:
    return (
        case.signals.seam_result.value,
        case.signals.severity.value,
        case.signals.failure_rate,
    )


def _downsample(cases: list[Case], target: int) -> list[Case]:
    """Deterministically thin ``cases`` to ``target`` rows, spread across the sorted axis."""
    ordered = sorted(cases, key=_sort_key)
    if len(ordered) <= target:
        return ordered
    stride = len(ordered) / target
    return [ordered[int(i * stride)] for i in range(target)]


def build_training(heldout: list[Case]) -> list[Case]:
    """Generate a route-balanced training set provably disjoint from ``heldout``.

    Every ``(seam, severity, rate)`` over the allowed rate regions is labeled by ``route_for``,
    dropped if :func:`contaminates_heldout` (band membership — impossible here by construction —
    or a near-duplicate of a held-out case), then the three routes are balanced to the minority
    count so accuracy cannot be inflated by the escalate-heavy majority. Deterministic.
    """
    candidates: list[Case] = []
    for seam in _SEAMS:
        for sev in _SEVERITIES:
            for rate in _training_rates():
                signals = TriageSignals(
                    failure_rate=rate, seam_result=seam, severity=sev
                )
                if contaminates_heldout(signals, heldout):
                    continue
                candidates.append(
                    _case(
                        rate, seam, sev, f"train {seam.value}/{sev.value} @ {rate:.3f}"
                    )
                )

    by_route: dict[Route, list[Case]] = {r: [] for r in Route}
    for case in candidates:
        by_route[case.route].append(case)
    target = min(len(v) for v in by_route.values())

    balanced: list[Case] = []
    for route in Route:  # fixed enum order → stable output
        balanced.extend(_downsample(by_route[route], target))
    return sorted(balanced, key=_sort_key)


def route_distribution(cases: list[Case]) -> dict[str, int]:
    """Count cases per route — for the honest report (class balance is visible)."""
    counts: dict[str, int] = {r.value: 0 for r in Route}
    for case in cases:
        counts[case.route.value] += 1
    return counts
