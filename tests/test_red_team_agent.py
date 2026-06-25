"""The Red-Team Agent (MA-01) — the §2 honesty test: an agent, not a for-loop.

THE load-bearing test (MA-00 §2/§5): flip what the early probes OBSERVE and the
agent's probe SEQUENCE must flip. Same observations → same sequence; different
observations → different sequence. If the sequence were identical regardless of
what it observed, this would be a loop in costume — the build would fail here.

Fast and deterministic: the agent's ``observe`` is injected with canned outcomes
(no Garak, no Ollama), so these tests exercise the POLICY directly.
"""

from __future__ import annotations

import shutil
from collections.abc import Mapping

import httpx
import pytest

from keystone.agents.red_team import (
    DEFAULT_BUDGET,
    PHASE_EXPLOIT,
    PHASE_SCOUT,
    PROBE_CATALOG,
    RECORDED_DEFENSE_PROFILE,
    Observe,
    choose_next,
    garak_observe,
    profile_observe,
    run_red_team,
)
from keystone.assurance.garak_probe import GarakError

# The two families the code recognizes — the agent's decision space spans both.
_LATENT = "latentinjection"
_PROMPT = "promptinject"


def _profile(through: str, blocked: str) -> Mapping[str, tuple[int, int]]:
    """A defense where every `through` probe lands and every `blocked` probe is caught."""
    profile: dict[str, tuple[int, int]] = {}
    for probe in PROBE_CATALOG[through]:
        profile[probe] = (8, 12)
    for probe in PROBE_CATALOG[blocked]:
        profile[probe] = (0, 12)
    return profile


def _observe(through: str, blocked: str) -> Observe:
    return profile_observe(_profile(through, blocked))


# --- THE honesty test (MA-00 §2) ----------------------------------------------


def test_sequence_flips_when_observations_flip() -> None:
    # Scenario 1: latentinjection gets through, promptinject is blocked.
    s1 = run_red_team(_observe(through=_LATENT, blocked=_PROMPT))
    # Scenario 2 (the inverse): promptinject gets through, latentinjection blocked.
    s2 = run_red_team(_observe(through=_PROMPT, blocked=_LATENT))

    # DIFFERENT observations → DIFFERENT sequence. This is the proof of agency:
    # the agent's choices are a function of what it observed, not a fixed list.
    assert s1.probe_sequence != s2.probe_sequence

    # And concretely: it escalates the family that got through and drops the other.
    assert s1.exploited_family == _LATENT
    assert s1.abandoned_families == (_PROMPT,)
    assert s2.exploited_family == _PROMPT
    assert s2.abandoned_families == (_LATENT,)


def test_same_observations_give_the_same_sequence() -> None:
    # SAME observations → SAME sequence: the policy is deterministic (so it replays).
    a = run_red_team(_observe(through=_LATENT, blocked=_PROMPT))
    b = run_red_team(_observe(through=_LATENT, blocked=_PROMPT))
    assert a.probe_sequence == b.probe_sequence


def test_choice_at_step_n_depends_on_earlier_outcomes() -> None:
    # The agent's escalation is driven by the outcomes it accumulated: after both
    # families are scouted, the next choice picks the family observed getting through.
    trace = run_red_team(_observe(through=_PROMPT, blocked=_LATENT))
    exploit_steps = [d for d in trace.decisions if d.phase == PHASE_EXPLOIT]
    assert exploit_steps, "the agent should escalate once it sees a family get through"
    # Every escalation targets the family that was observed getting through.
    assert all(d.chosen_family == _PROMPT for d in exploit_steps)


# --- the agency bar's structural requirements (MA-00 §2.1-2.4) -----------------


def test_decision_space_is_two_families_each_with_at_least_two_probes() -> None:
    # ≥2 families, ≥2 probes/family — "choose" is genuinely meaningful (MA-00 §2.3).
    assert len(PROBE_CATALOG) >= 2
    assert all(len(probes) >= 2 for probes in PROBE_CATALOG.values())
    # The real Garak v0.15.1 in-family surface: 23 probes total.
    assert sum(len(p) for p in PROBE_CATALOG.values()) == 23


def test_agent_scouts_both_families_before_exploiting() -> None:
    trace = run_red_team(_observe(through=_LATENT, blocked=_PROMPT))
    # It establishes an observation for BOTH families (scout phase) first.
    assert set(trace.scouted_families) == {_LATENT, _PROMPT}
    first_exploit = next(
        i for i, d in enumerate(trace.decisions) if d.phase == PHASE_EXPLOIT
    )
    assert all(d.phase == PHASE_SCOUT for d in trace.decisions[:first_exploit])


def test_agent_stops_when_nothing_gets_through() -> None:
    # If the defense holds against BOTH families, there is no exploit path: the agent
    # scouts each once and stops — it does not keep firing into a wall (honest).
    blocked_everywhere = {p: (0, 12) for fam in PROBE_CATALOG.values() for p in fam}
    trace = run_red_team(profile_observe(blocked_everywhere))
    assert trace.exploited_family is None
    assert {d.phase for d in trace.decisions} == {PHASE_SCOUT}
    assert len(trace.decisions) == len(PROBE_CATALOG)  # one scout per family, then stop


def test_choose_next_is_a_pure_function_of_observations() -> None:
    # With no observations the policy scouts the first family's lead probe.
    assert choose_next([]) == (PROBE_CATALOG[_LATENT][0], PHASE_SCOUT)


def test_budget_bounds_the_run() -> None:
    trace = run_red_team(_observe(through=_LATENT, blocked=_PROMPT), budget=3)
    assert len(trace.decisions) == 3
    default = run_red_team(_observe(through=_LATENT, blocked=_PROMPT))
    assert len(default.decisions) == DEFAULT_BUDGET


# --- the recorded defense profile (the offline demo trace) --------------------


def test_recorded_profile_drives_a_real_adaptive_run() -> None:
    trace = run_red_team(profile_observe(RECORDED_DEFENSE_PROFILE))
    # The offline recording is a genuine adaptive run: it escalates the family that
    # gets through (latentinjection, anchored on the real 10/12 fixture) and drops
    # the blocked one — the same shape the live agent would produce.
    assert trace.exploited_family == _LATENT
    assert trace.abandoned_families == (_PROMPT,)
    # Anchored to the REAL captured Garak fixture: lead probe failure_rate = 10/12.
    assert trace.decisions[0].outcome.fails == 10
    assert trace.decisions[0].outcome.total_evaluated == 12


# --- live adaptive run (slow; skips cleanly if garak/Ollama unavailable) -------


def _ollama_up() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2.0)
    except httpx.HTTPError:
        return False
    return True


@pytest.mark.slow
def test_live_agent_runs_and_observes_real_garak() -> None:
    # The LIVE path (MA-00 §4): the agent genuinely fires real Garak scans per probe
    # and adapts on the real outcomes. Budget 2 = scout both families (bounded
    # runtime); the fast tests above prove the adaptation. Skips cleanly offline.
    if shutil.which("garak") is None and shutil.which("uv") is None:
        pytest.skip("garak CLI not available")
    if not _ollama_up():
        pytest.skip("Ollama not running")
    try:
        trace = run_red_team(
            garak_observe(report_prefix="ma01_test_live", prompt_cap=4), budget=2
        )
    except GarakError as exc:
        pytest.skip(f"garak unavailable: {exc}")

    # It scouted both families on real measurements, and the choices are real.
    assert set(trace.scouted_families) == set(PROBE_CATALOG)
    assert all(d.outcome.total_evaluated > 0 for d in trace.decisions)
