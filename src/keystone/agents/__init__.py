"""Orchestration — NeMo Agent Toolkit (`nvidia-nat`) workflows.

The orchestration entry point. TODAY this package holds DETERMINISTIC orchestration:
NAT sequences fixed workflow stages (the chassis fan-out, the assurance loop, the
Layer-1 milestone arc) — no reasoning, and no agent chooses the next step (the stubs'
own docstrings say "no LLM — just orchestration"). The package name looks FORWARD: this
is where the genuine agents being added in Movements A/B — the offensive Red-Team agent
(observe -> reason -> adapt over the Garak probe library) and the supervisory Triage
agent — will sit, within this orchestration. Until those land, nothing here is an agent
in the reasoning sense.

May depend inward on the deterministic core; the core must not depend on it.

MA-01 makes this package's forward-promise TRUE: ``red_team`` is the first genuine
agent — an adaptive offensive policy that observes probe outcomes and adapts its
next probe choice (the MA-00 §2 honesty test). It is an agent, framed honestly as a
policy (not an LLM).

MB-01 adds the second: ``triage`` — a supervisory triage policy that routes a finding
(remediate / accept / escalate) over the INTERPLAY of its signals (the MB-00 §2 test).
With the offensive worker (``red_team``) and this supervisor, Keystone is honestly a
**multi-agent system** — two agents, a supervisor–worker topology, verifiable in code.
Both are agents, framed honestly as policies (not LLMs).
"""

from __future__ import annotations

from .red_team import (
    DEFAULT_BUDGET,
    MECHANISM,
    PROBE_CATALOG,
    RECORDED_DEFENSE_PROFILE,
    Observe,
    ProbeOutcome,
    RedTeamDecision,
    RedTeamTrace,
    choose_next,
    garak_observe,
    profile_observe,
    run_red_team,
)
from .triage import (
    ACTION_FLOOR,
    FindingSeverity,
    Route,
    SeamClassification,
    TriageDecision,
    TriageSignals,
    route_for,
    triage,
)

# MECHANISM is the red-team agent's; the triage agent's is TRIAGE_MECHANISM.
from .triage import MECHANISM as TRIAGE_MECHANISM

__all__ = [
    "ACTION_FLOOR",
    "DEFAULT_BUDGET",
    "MECHANISM",
    "PROBE_CATALOG",
    "RECORDED_DEFENSE_PROFILE",
    "TRIAGE_MECHANISM",
    "FindingSeverity",
    "Observe",
    "ProbeOutcome",
    "RedTeamDecision",
    "RedTeamTrace",
    "Route",
    "SeamClassification",
    "TriageDecision",
    "TriageSignals",
    "choose_next",
    "garak_observe",
    "profile_observe",
    "route_for",
    "run_red_team",
    "triage",
]
