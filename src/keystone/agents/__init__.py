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

OPT-A-01 takes the triage supervisor **live** (opt-in): ``live_triage`` reasons the
route with a local LLM (qwen2.5:3b) over the same signals, constrained to the same
3-option space, with the policy as a proven fallback and an honest reasoner tag on
every decision. Live is strictly additive — the offline default is untouched.
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
    POLICY_FALLBACK_REASONER,
    POLICY_REASONER,
    FindingSeverity,
    LlmReasoner,
    LlmRouteChoice,
    Route,
    SeamClassification,
    TriageDecision,
    TriageSignals,
    build_live_prompt,
    live_triage,
    llm_reasoner_tag,
    mechanism_for,
    ollama_reasoner,
    parse_llm_choice,
    route_for,
    triage,
    triage_live,
)

# MECHANISM is the red-team agent's; the triage agent's is TRIAGE_MECHANISM.
from .triage import MECHANISM as TRIAGE_MECHANISM

__all__ = [
    "ACTION_FLOOR",
    "DEFAULT_BUDGET",
    "MECHANISM",
    "POLICY_FALLBACK_REASONER",
    "POLICY_REASONER",
    "PROBE_CATALOG",
    "RECORDED_DEFENSE_PROFILE",
    "TRIAGE_MECHANISM",
    "FindingSeverity",
    "LlmReasoner",
    "LlmRouteChoice",
    "Observe",
    "ProbeOutcome",
    "RedTeamDecision",
    "RedTeamTrace",
    "Route",
    "SeamClassification",
    "TriageDecision",
    "TriageSignals",
    "build_live_prompt",
    "choose_next",
    "garak_observe",
    "live_triage",
    "llm_reasoner_tag",
    "mechanism_for",
    "ollama_reasoner",
    "parse_llm_choice",
    "profile_observe",
    "route_for",
    "run_red_team",
    "triage",
    "triage_live",
]
