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

from collections.abc import Sequence
from dataclasses import dataclass
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


@dataclass(frozen=True)
class Remediation:
    """One menu entry: a named remediation, the seam side it acts on, and a one-liner.

    A descriptive catalog entry (not yet a uniform callable — MC-01's defense agent will
    dispatch on it); the point of MC-PRE-01 is that ``REMEDIATION_MENU`` holds ≥2 entries
    on DIFFERENT sides, so a future agent has a genuine choice to reason over.
    """

    control: str
    side: SeamSide
    summary: str


GUARDRAIL_PATCH = Remediation(
    control=GUARDRAIL_PATCH_CONTROL,
    side=SeamSide.AI,
    summary="Block memo prompt-injection at the NeMo Guardrails input rail (KS-0302).",
)
FINANCIAL_TIGHTENING = Remediation(
    control=FINANCIAL_TIGHTENING_CONTROL,
    side=SeamSide.FINANCIAL,
    summary=(
        "Tighten FATF detection (STRICT_THRESHOLDS) so a transfer that slipped the "
        "baseline is flagged — memo-blind, the financial-side second line of defense."
    ),
)

# The menu: ≥2 genuinely-distinct remediations, one per side of the seam. What MC-00's
# defense agent will choose over; today it is the catalog, no agent chooses yet.
REMEDIATION_MENU: tuple[Remediation, ...] = (GUARDRAIL_PATCH, FINANCIAL_TIGHTENING)


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
