"""The Defense Agent (MC-01) — Keystone's third genuine agent.

A **supervisory defense policy** (MC-00 §1/§3): it reads a finding's already-computed,
two-sided strength and CHOOSES which remediation the finding warrants — **(a)** block the
prompt-injection at the AI-side guardrail rail, or **(c)** tighten the money-side FATF
detection — then applies the chosen remediation through the uniform
:class:`keystone.assurance.remediation.Remediation` interface.

**Honest framing (MC-00 §1).** This is an *adaptive policy*, NOT an LLM agent. The choice is a
transparent function of the finding (:func:`choose_remediation`), not model inference — OPT-A-01b
proved a 3B model cannot reason a bounded choice reliably, so LLM-reasoned remediation choice is
compute-gated. Mechanism label: *"adaptive defense policy (finding-dependent remediation
selection; not an LLM)."*

**The decision space is real (MC-00 §0, gate).** The two signals are *independent* measurements:
``failure_rate`` is the Red-Team's landed-exploit rate (a property of the model + probe, from a
Garak scan) and ``financial_gap`` is whether a transaction slips baseline FATF detection but is
caught once tightened (a property of amounts/thresholds, memo-blind). A finding can be strong on
one side and weak on the other, so the choice genuinely FLIPS — proven in ``tests/test_defense_agent.py``.

**The memo-blind boundary (MC-00 §4, sacred).** The agent reads :class:`DefenseSignals` — the
three already-computed signals — and NEVER the attack channel. Like the Triage Agent it defines
its own value enums (reused from ``keystone.agents.triage``) so it imports nothing from the
detection framework. Applying (a) may let the guardrail rail read the memo (the AI-side defense
is allowed to — it is not the crime detector), but the agent's CHOICE never does.

**Scope (MC-00 §5).** MC-01 STOPS at *applying* the remediation; it does NOT re-scan or close the
offense↔defense loop — the uniform interface's ``retest_via`` handle is built loop-ready for MC-02.
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from keystone.agents.triage import FindingSeverity, SeamClassification
from keystone.assurance.remediation import (
    FINANCIAL_TIGHTENING,
    GUARDRAIL_PATCH,
    Remediation,
    RemediationContext,
    RemediationOutcome,
)

# Below this exploit rate the injection is "contained" — not a live AI-side risk. Mirrors the
# Triage Agent's action floor: the same noise-floor concept, applied to the defense choice.
DEFENSE_FLOOR = 0.10

# Reasoner tag — the honesty guarantee (mirror OPT-A-00 §3). Defense is policy-only in MC-01;
# there is no LLM path (compute-gated), so the tag is always the policy.
POLICY_REASONER = "policy"

# Honest one-line mechanism, surfaced in the trace / UI / paper.
MECHANISM = (
    "adaptive defense policy (finding-dependent remediation selection; not an LLM)"
)


def mechanism_for(reasoner: str) -> str:
    """The honest mechanism label matching the reasoner that ran (policy-only in MC-01)."""
    return MECHANISM


class DefenseSignals(BaseModel):
    """The OBSERVED STATE: a finding's already-computed two-sided strength (read-only).

    Memo-blind (MC-00 §4): the agent READS these — it never recomputes them and never reaches
    the attack channel. ``failure_rate`` is the AI-side strength (the Red-Team's landed-exploit
    rate); ``financial_gap`` is the financial-side strength (True when a transaction slips
    baseline detection but STRICT_THRESHOLDS catches it — money the detection is missing);
    ``seam_result`` / ``severity`` enrich the record and rationale.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    failure_rate: float
    financial_gap: bool
    seam_result: SeamClassification
    severity: FindingSeverity


@dataclass(frozen=True)
class DefenseDecision:
    """The agent's decision: the chosen remediation + its applied outcome + why (audit trail).

    A faithful capture of a genuine defense decision, replayed deterministically (the policy is
    a pure function of the observed signals, so the same finding always chooses the same fix).
    """

    signals: DefenseSignals
    remediation: Remediation  # the chosen menu entry (control + seam side)
    outcome: RemediationOutcome  # the uniform apply() result
    rationale: str
    reasoner: str = POLICY_REASONER


def choose_remediation(signals: DefenseSignals) -> Remediation:
    """THE reasoning step: choose the remediation the finding's two-sided strength warrants.

    Transparent policy (MC-00 §3). Both signals matter — (c) is reached ONLY when the money is
    provably slipping detection AND the injection is contained (the residual risk is money
    movement, so tighten the money-side); otherwise (a) — the injection is live (close the AI
    hole, the root cause upstream of the transfer, correct even if the money-side also has a
    gap), or neither hole is open (harden the input rail as the structural default).
    """
    ai_live = signals.failure_rate >= DEFENSE_FLOOR
    if signals.financial_gap and not ai_live:
        return FINANCIAL_TIGHTENING  # (c): money slips, injection contained
    return GUARDRAIL_PATCH  # (a): injection live, or the default hardening


def _rationale(signals: DefenseSignals) -> str:
    """Plain-language WHY for the chosen remediation — grounded in the two-sided strength."""
    rate = f"{signals.failure_rate:.0%}"
    floor = f"{DEFENSE_FLOOR:.0%}"
    ai_live = signals.failure_rate >= DEFENSE_FLOOR
    if signals.financial_gap and not ai_live:
        return (
            f"Injection contained ({rate} exploit, below the {floor} floor) but the financial "
            f"detection is provably missing a transaction — tighten the money-side (c): the "
            f"residual risk is money slipping AML thresholds, not the model."
        )
    if ai_live:
        gap_note = (
            " — even though the money-side also shows a gap"
            if signals.financial_gap
            else ""
        )
        return (
            f"Injection is live ({rate} exploit, at or above the {floor} floor) — close the "
            f"AI-side hole at the input rail (a): the root-cause control, upstream of the "
            f"transfer{gap_note}."
        )
    return (
        f"No live injection ({rate}, below the {floor} floor) and no detection gap — harden the "
        f"AI input rail (a) as the structural default; the memo channel is the vulnerability class."
    )


def defend(
    signals: DefenseSignals, *, context: RemediationContext | None = None
) -> DefenseDecision:
    """Run the agent: observe (signals) → reason (policy) → choose → apply → record.

    Chooses the remediation via :func:`choose_remediation`, then applies it through the uniform
    interface. The route is a pure function of the observed signals — the property the flip /
    determinism tests exercise. ``context`` (the run context: the tx stream for (c), the
    operative-tx handle for (a)) is injected; it does NOT feed the CHOICE, only the application.
    """
    chosen = choose_remediation(signals)
    outcome = chosen.apply(context if context is not None else RemediationContext())
    return DefenseDecision(
        signals=signals,
        remediation=chosen,
        outcome=outcome,
        rationale=_rationale(signals),
        reasoner=POLICY_REASONER,
    )
