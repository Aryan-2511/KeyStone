"""Build the Defense Agent's recorded remediation choice from a genuine run (MC-01).

The `defense` block of the `RunResult` is DERIVED by actually RUNNING the Defense Agent
(`keystone.agents.defense.defend`) over the finding's two-sided strength — never hand-authored.
The defender reads the AI-side strength (`failure_rate`, from the MA-01 Red-Team trace) and the
financial-side gap (does a transaction slip baseline detection but get caught once tightened,
computed memo-blind from the stream), and CHOOSES which remediation the finding warrants —
(a) block the prompt at the guardrail rail, or (c) tighten the money-side detection — then
applies it through the uniform interface.

This module is the DEMO/INTEGRATION translation layer (MC-00 §4): it maps the real framework
`SeamResult` / FATF `Severity` onto the agent's value enums and computes the memo-blind
`financial_gap` — precisely so the AGENT need not (and must not) import the detection path.
The agent reasons over the already-computed signals; it never reaches the attack channel.

Boundary: lives in `keystone.demo`; the core never imports it (import-linter KEPT).
"""

from __future__ import annotations

from collections.abc import Sequence

from keystone.agents.defense import (
    DEFENSE_FLOOR,
    DefenseSignals,
    defend,
    mechanism_for,
)
from keystone.agents.triage import FindingSeverity, SeamClassification
from keystone.assurance.framework import SeamResult
from keystone.assurance.remediation import (
    REMEDIATION_MENU,
    RemediationContext,
    financial_detection_gap,
)
from keystone.core.fatf.models import Severity
from keystone.core.transactions import Transaction

from .run_result import DefenseView


def build_defense_view(
    *,
    failure_rate: float,
    seam_result: SeamResult,
    severity: Severity,
    stream: Sequence[Transaction],
    operative_tx_id: str | None = None,
) -> DefenseView:
    """Run the Defense Agent over the finding's two-sided strength and project it.

    A REAL agentic run: the defender observes the AI-side `failure_rate` and the memo-blind
    financial-side gap (`financial_detection_gap(stream)` — transactions baseline misses that
    STRICT_THRESHOLDS catches), reasons via the transparent policy, chooses a remediation, and
    applies it through the uniform interface. `financial_gap` is computed HERE (the integration
    layer) from the real stream, never by the agent — the agent stays memo-blind.
    """
    gap = financial_detection_gap(stream)
    signals = DefenseSignals(
        failure_rate=failure_rate,
        financial_gap=bool(gap),
        seam_result=SeamClassification(seam_result.value),
        severity=FindingSeverity(severity.value),
    )
    decision = defend(
        signals,
        context=RemediationContext(
            stream=tuple(stream), operative_tx_id=operative_tx_id
        ),
    )
    return DefenseView(
        control=decision.remediation.control,
        side=decision.remediation.side.value,
        failure_rate=signals.failure_rate,
        financial_gap=signals.financial_gap,
        seam_result=signals.seam_result.value,
        severity=signals.severity.value,
        rationale=decision.rationale,
        remediations_available=tuple(r.control for r in REMEDIATION_MENU),
        mechanism=mechanism_for(decision.reasoner),
        reasoner=decision.reasoner,
        summary=decision.outcome.summary,
        detail=decision.outcome.detail,
        retest_via=decision.outcome.retest_via,
        verified_offline=decision.outcome.verified_offline,
    )


# The policy's action floor, surfaced for the view/UI transparency (below this exploit rate
# the injection is "contained" and the money-side becomes the deciding signal).
DEFENSE_ACTION_FLOOR = DEFENSE_FLOOR
