"""Build the Triage Agent's recorded routing decision from a genuine run (MB-01).

The `triage` block of the `RunResult` is DERIVED by actually RUNNING the Triage Agent
(`keystone.agents.triage.triage`) over the finding's already-computed signals — never
hand-authored. The supervisor reads three signals others computed: the offense worker's
strongest landed exploit (`failure_rate`, from the MA-01 Red-Team trace), how the seam
classifies (`seam_result`, from the seam framework's REGISTERED_PAIRS), and the mapped
`severity` (from the L1 FATF finding). It routes the finding to one of three actions.

This module is the DEMO/INTEGRATION translation layer (MB-00 §4): it is allowed to read
both the seam framework and the core FATF types and map them onto the agent's own value
signals — precisely so the AGENT need not (and must not) import the detection path. The
runner hands this builder the three already-computed values; the agent reasons over them.

Boundary: lives in `keystone.demo`; the core never imports it (import-linter KEPT). The
agent it runs is a supervisor with no path to the detector or the attack channel (§4).
"""

from __future__ import annotations

from keystone.agents.triage import (
    ACTION_FLOOR,
    MECHANISM,
    FindingSeverity,
    Route,
    SeamClassification,
    TriageSignals,
    triage,
)
from keystone.assurance.framework import SeamResult
from keystone.core.fatf.models import Severity

from .run_result import TriageView


def build_triage_view(
    *,
    failure_rate: float,
    seam_result: SeamResult,
    severity: Severity,
) -> TriageView:
    """Run the Triage Agent over the finding's already-computed signals and project it.

    A REAL agentic run: the supervisor observes the three signals (mapped from the real
    framework `SeamResult` / FATF `Severity` onto the agent's value enums — by value,
    parity-locked), reasons via its policy over their interplay, and routes the finding.
    The recorded decision replays deterministically (the policy is a pure function of the
    observed signals — MB-00 §4).
    """
    decision = triage(
        TriageSignals(
            failure_rate=failure_rate,
            seam_result=SeamClassification(seam_result.value),
            severity=FindingSeverity(severity.value),
        )
    )
    return TriageView(
        route=decision.route.value,
        failure_rate=decision.signals.failure_rate,
        seam_result=decision.signals.seam_result.value,
        severity=decision.signals.severity.value,
        rationale=decision.rationale,
        action_floor=ACTION_FLOOR,
        routes_available=tuple(r.value for r in Route),
        mechanism=MECHANISM,
    )
