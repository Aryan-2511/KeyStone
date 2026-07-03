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
    FindingSeverity,
    Route,
    SeamClassification,
    TriageSignals,
    live_triage,
    mechanism_for,
    triage,
)
from keystone.assurance.framework import SeamResult
from keystone.core.fatf.models import Severity
from keystone.llm.inference import Backend

from .run_result import TriageView


def build_triage_view(
    *,
    failure_rate: float,
    seam_result: SeamResult,
    severity: Severity,
    live: bool = False,
    backend: Backend | None = None,
) -> TriageView:
    """Run the Triage Agent over the finding's already-computed signals and project it.

    A REAL agentic run: the supervisor observes the three signals (mapped from the real
    framework `SeamResult` / FATF `Severity` onto the agent's value enums — by value,
    parity-locked), reasons, and routes the finding.

    Default (``live=False``): the transparent policy reasons — a pure function of the
    observed signals, so the recorded decision replays deterministically (MB-00 §4).
    Opt-in (``live=True``): a live LLM (qwen2.5:3b via Ollama) reasons the route over the
    SAME signals, constrained to the same 3-option space, with the policy as a proven
    fallback (OPT-A-01). Either way the projected `reasoner`/`mechanism` state which
    reasoner actually ran — a fallback is never reported as an LLM decision (OPT-A-00 §3).
    """
    signals = TriageSignals(
        failure_rate=failure_rate,
        seam_result=SeamClassification(seam_result.value),
        severity=FindingSeverity(severity.value),
    )
    decision = live_triage(signals, backend=backend) if live else triage(signals)
    return TriageView(
        route=decision.route.value,
        failure_rate=decision.signals.failure_rate,
        seam_result=decision.signals.seam_result.value,
        severity=decision.signals.severity.value,
        rationale=decision.rationale,
        action_floor=ACTION_FLOOR,
        routes_available=tuple(r.value for r in Route),
        mechanism=mechanism_for(decision.reasoner),
        reasoner=decision.reasoner,
    )
