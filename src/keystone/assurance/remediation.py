"""The remediation menu (MC-PRE-01) — ≥2 genuinely-distinct fixes, one per seam side.

The remediation probe (`remediation_probe.md`) returned MENU-FIRST: to make a defense
agent honest (Movement C), the system must offer a real CHOICE among distinct remediations,
not one mechanism dressed as a menu. This module supplies that second, genuinely-distinct
option and catalogs the menu — it does NOT add an agent (that is MC-01).

The two remediations act on OPPOSITE sides of the L2↔L1 seam:

* **(a) GUARDRAIL_PATCH — AI side.** Block the memo prompt-injection at the NeMo Guardrails
  input rail (KS-0302, :func:`keystone.assurance.guard.run_guarded_agent`). Unchanged here;
  referenced by name only.
* **(c) FINANCIAL_TIGHTENING — financial side.** Re-run the SAME memo-blind FATF engine with
  a stricter threshold profile (:data:`keystone.core.fatf.STRICT_THRESHOLDS`), so a transfer
  that slipped the baseline detection is flagged. Different layer, different outcome, and a
  finding can call for one over the other — a real, finding-dependent choice.

**Memo-blind boundary (sacred).** (c) NEVER reads the attack channel: it calls the same
:func:`keystone.core.fatf.detect`, which is memo-blind by construction (it keys on amounts /
timing / accounts, never ``Transaction.memo``). Tightening only changes the threshold numbers.
This module lives in the ``keystone.assurance`` edge and imports ``keystone.core`` (allowed);
the core never imports it (import-linter KEPT).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum

from keystone.core.fatf import STRICT_THRESHOLDS, Finding, detect
from keystone.core.transactions import Transaction


class SeamSide(StrEnum):
    """Which side of the L2↔L1 seam a remediation acts on — what makes the menu distinct."""

    AI = "ai"  # the L2 prompt / agent side (a): block the injection
    FINANCIAL = "financial"  # the L1 money / detection side (c): flag the transfer


# Control names. (a) mirrors :data:`keystone.assurance.loop.CONTROL_NAME` EXACTLY — we
# reference the existing rail, never redefine or change it (a test pins the equality).
GUARDRAIL_PATCH_CONTROL = "nemo-guardrails-input-rail"
FINANCIAL_TIGHTENING_CONTROL = "fatf-strict-thresholds"

# Re-test handles (MC-00 §2): how MC-02's adversarial loop would RE-TEST each remediation.
# Named here so the interface is loop-ready; MC-01 does NOT wire the loop.
RETEST_GUARDED_SCAN = (
    "scan_guarded_agent"  # (a): re-scan the guarded endpoint with Garak
)
RETEST_STRICT_DETECT = "detect_strict"  # (c): re-run detection at STRICT_THRESHOLDS


# --- the FATF-tightening mechanism (c), also the MC-PRE-01 proof surface -------


def tighten_financial_detection(stream: Sequence[Transaction]) -> list[Finding]:
    """Apply remediation (c): re-run the memo-blind FATF engine at STRICT_THRESHOLDS.

    Same :func:`keystone.core.fatf.detect` (never reads the memo), stricter numbers — the
    financial-side second line of defense. Returns every finding under the tightened profile.
    """
    return detect(stream, STRICT_THRESHOLDS)


def newly_flagged_by_tightening(stream: Sequence[Transaction]) -> list[Finding]:
    """The findings remediation (c) catches that the BASELINE detection MISSES.

    The proof (c) is a genuine second line and not a no-op: every finding present under
    ``STRICT_THRESHOLDS`` but absent under ``DEFAULT_THRESHOLDS``, keyed by (typology, tx
    ids). An empty list would mean tightening catches nothing new — (c) would not be
    distinct in practice on this stream.
    """
    baseline = {(f.typology, f.transaction_ids) for f in detect(stream)}
    return [
        finding
        for finding in tighten_financial_detection(stream)
        if (finding.typology, finding.transaction_ids) not in baseline
    ]


def financial_detection_gap(stream: Sequence[Transaction]) -> frozenset[str]:
    """Tx ids the BASELINE misses ENTIRELY (no finding) that STRICT_THRESHOLDS catches.

    The Defense Agent's memo-blind financial-side signal: a non-empty gap means money is
    slipping detection (a transfer covered by no baseline finding but caught once tightened)
    — the residual risk remediation (c) closes. Distinct from
    :func:`newly_flagged_by_tightening` (finding-level, which also re-flags already-covered
    transactions under a stricter typology); this is TRANSACTION COVERAGE — what slips through.
    """
    baseline = {tid for f in detect(stream) for tid in f.transaction_ids}
    strict = {
        tid for f in detect(stream, STRICT_THRESHOLDS) for tid in f.transaction_ids
    }
    return frozenset(strict - baseline)


# --- the uniform remediation interface (MC-00 §2) -----------------------------


@dataclass(frozen=True)
class RemediationContext:
    """What a remediation's ``apply`` may draw on — the RUN context, not the agent's choice.

    The Defense Agent CHOOSES on the finding's signals (memo-blind); dispatch then hands the
    chosen remediation this context. (c) reads ``stream`` (re-detect); (a) uses
    ``operative_tx_id`` as its re-test handle. Carrying the stream here does NOT make the
    agent's CHOICE depend on it — the choice is made before dispatch, on signals alone.
    """

    stream: tuple[Transaction, ...] = ()
    operative_tx_id: str | None = None


@dataclass(frozen=True)
class RemediationOutcome:
    """The uniform result of applying a remediation — abstracts the action, keeps the side.

    ``verified_offline`` is honestly asymmetric: (c) is a pure offline detection change so its
    effect is known now (True/False); (a) is an AI-path control whose effect needs a re-scan,
    so it is ``None`` here — verified by MC-02's loop via ``retest_via``.
    """

    control: str
    side: SeamSide
    summary: str
    detail: tuple[str, ...]  # concrete artifacts, e.g. the tx ids (c) newly covers
    retest_via: (
        str  # the handle MC-02's loop re-tests through (loop-ready, not wired here)
    )
    verified_offline: bool | None


def _apply_guardrail(context: RemediationContext) -> RemediationOutcome:
    """(a) AI-side: enforce the NeMo Guardrails input rail on the memo channel (KS-0302).

    MC-01 records the control applied and the re-test handle; it does NOT run the live model
    or re-scan (that closes the loop — MC-02), so the rail's effect on THIS finding is
    ``verified_offline=None`` (verified by the MC-02 re-scan). (a)'s behaviour is unchanged.
    """
    return RemediationOutcome(
        control=GUARDRAIL_PATCH_CONTROL,
        side=SeamSide.AI,
        summary="Enforce the NeMo Guardrails input rail on the memo channel (KS-0302).",
        detail=(context.operative_tx_id,) if context.operative_tx_id else (),
        retest_via=RETEST_GUARDED_SCAN,
        verified_offline=None,  # AI-path effect needs the MC-02 re-scan; not claimed now
    )


def _apply_financial_tightening(context: RemediationContext) -> RemediationOutcome:
    """(c) financial-side: re-run memo-blind detection at STRICT_THRESHOLDS; report the catch.

    Fully offline and deterministic — its effect (which transactions the tightening newly
    covers) is known now, so ``verified_offline`` is a real bool.
    """
    gap = sorted(financial_detection_gap(context.stream))
    return RemediationOutcome(
        control=FINANCIAL_TIGHTENING_CONTROL,
        side=SeamSide.FINANCIAL,
        summary="Tighten FATF detection (STRICT_THRESHOLDS) — memo-blind re-detection.",
        detail=tuple(gap),
        retest_via=RETEST_STRICT_DETECT,
        verified_offline=bool(gap),
    )


@dataclass(frozen=True)
class Remediation:
    """One menu entry: a named remediation, the seam side it acts on, and its ``apply``.

    ``apply`` is the uniform interface (MC-00 §2): the Defense Agent selects a Remediation on
    the finding, then calls ``apply(context)`` — same signature for both, so the dispatch is
    uniform, never a signature-branch masquerading as a choice. ``side`` keeps the seam-side
    difference visible on every entry and outcome.
    """

    control: str
    side: SeamSide
    summary: str
    apply: Callable[[RemediationContext], RemediationOutcome] = field(compare=False)


GUARDRAIL_PATCH = Remediation(
    control=GUARDRAIL_PATCH_CONTROL,
    side=SeamSide.AI,
    summary="Block memo prompt-injection at the NeMo Guardrails input rail (KS-0302).",
    apply=_apply_guardrail,
)
FINANCIAL_TIGHTENING = Remediation(
    control=FINANCIAL_TIGHTENING_CONTROL,
    side=SeamSide.FINANCIAL,
    summary=(
        "Tighten FATF detection (STRICT_THRESHOLDS) so a transfer that slipped the "
        "baseline is flagged — memo-blind, the financial-side second line of defense."
    ),
    apply=_apply_financial_tightening,
)

# The menu: ≥2 genuinely-distinct remediations, one per side of the seam. What the MC-01
# defense agent chooses over via the uniform ``apply`` interface.
REMEDIATION_MENU: tuple[Remediation, ...] = (GUARDRAIL_PATCH, FINANCIAL_TIGHTENING)
