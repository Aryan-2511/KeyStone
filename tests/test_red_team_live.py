"""The live Red-Team Agent (OPT-A-02) — the honesty tests (OPT-A-02-00 §5).

The Red-Team Agent gains an opt-in LIVE mode: it runs its full policy-selected probe
sequence as REAL Garak scans, with the recorded defense profile as a proven fallback.
These tests pin the honesty guarantees the design fixed BEFORE code, mirroring OPT-A-01:

1. **Source-honesty** — every trace tags WHERE its outcomes came from (``garak_live`` vs
   ``recorded_profile``); a fallback is NEVER reported as a live scan.
2. **Fallback** — an unavailable / errored Garak scan falls back to a complete recorded
   run, tagged ``recorded_profile`` — never a fabricated "live" outcome.
3. **§2 agency preserved** — the selection policy still adapts to observed outcomes
   (a family gets through vs blocked → the sequence flips), now over live-capable observes.
4. **Offline default unchanged** — the recorded path produces identical results with NO
   Garak (the front door works with no live infra).

Fast-gate tests inject a fake observe so the gate never runs Garak or a network. The one
real-Garak check is ``slow`` and skips cleanly if Garak / Ollama are unavailable.
"""

from __future__ import annotations

import shutil
import sys

import httpx
import pytest

from keystone.agents.red_team import (
    DEEP_PROBES,
    GARAK_LIVE_SOURCE,
    PROBE_CATALOG,
    RECORDED_DEFENSE_PROFILE,
    RECORDED_PROFILE_SOURCE,
    SCOPE_FULL,
    SCOPE_TRACTABLE,
    ProbeOutcome,
    family_of,
    is_deep,
    live_red_team,
    mechanism_for,
    tractable_catalog,
)
from keystone.assurance.garak_probe import GarakError
from keystone.demo import build_run_result
from keystone.demo.red_team import build_red_team_view
from keystone.demo.runner import LiveModes
from keystone.llm.inference import BackendUnreachableError

# --- fakes: injected so the fast gate never runs Garak ------------------------


def _unavailable_observe(probe: str) -> ProbeOutcome:
    """A Garak observe that always fails, as if Garak/the target were down."""
    raise GarakError("garak unavailable (stubbed)")


def _profile_observe(probe: str) -> ProbeOutcome:
    """A successful live observe mirroring the recorded profile (latent through)."""
    fails, total = RECORDED_DEFENSE_PROFILE[probe]
    return ProbeOutcome(
        probe=probe, family=family_of(probe), fails=fails, total_evaluated=total
    )


def _flipped_observe(probe: str) -> ProbeOutcome:
    """A posture where ONLY promptinject gets through (latent blocked) — to test the flip."""
    fam = family_of(probe)
    fails = 8 if fam == "promptinject" else 0
    return ProbeOutcome(probe=probe, family=fam, fails=fails, total_evaluated=12)


# --- 1. source-honesty (OPT-A-02-00 §3/§5) ------------------------------------


def test_successful_live_scan_records_garak_live() -> None:
    trace = live_red_team(observe=_profile_observe)
    assert trace.source == GARAK_LIVE_SOURCE
    assert len(trace.decisions) > 0


def test_unavailable_garak_records_recorded_profile_not_live() -> None:
    # THE guarantee: a failed scan falls back to the recorded profile and is tagged the
    # fallback source — never claimed as a live scan.
    trace = live_red_team(observe=_unavailable_observe)
    assert trace.source == RECORDED_PROFILE_SOURCE


def test_mechanism_label_matches_the_source() -> None:
    # The human mechanism label must match the machine tag (never say "REAL Garak scans"
    # for a recorded run, or vice versa).
    assert "REAL Garak scans" in mechanism_for(GARAK_LIVE_SOURCE)
    assert "REAL Garak" not in mechanism_for(RECORDED_PROFILE_SOURCE)
    assert "not an LLM" in mechanism_for(RECORDED_PROFILE_SOURCE)


# --- 2. fallback produces a complete, valid trace -----------------------------


def test_fallback_produces_a_complete_valid_trace() -> None:
    # The fallback is the safety architecture: a valid, complete trace is ALWAYS produced,
    # never a fabricated live outcome or a half-run.
    live = live_red_team(observe=_profile_observe)
    fallback = live_red_team(observe=_unavailable_observe)
    # Same policy, same budget → the fallback runs the same full sequence, just recorded.
    assert fallback.probe_sequence == live.probe_sequence
    assert fallback.exploited_family == "latentinjection"
    assert all(d.outcome.total_evaluated > 0 for d in fallback.decisions)


def test_full_sequence_runs_the_policy_not_a_subset_cap() -> None:
    # "Full selected sequence" (task): the policy's own stop (choose_next → None, when
    # every probe has been tried) ends the run, not the budget. Give it MORE budget than
    # the whole decision space and it still stops at the space size — the cap never bites.
    # This is the FULL scope (the --deep run), which exercises the whole catalog.
    total_probes = sum(len(v) for v in PROBE_CATALOG.values())
    trace = live_red_team(
        observe=_profile_observe, budget=total_probes + 5, scope=SCOPE_FULL
    )
    assert trace.scan_scope == SCOPE_FULL
    assert len(trace.decisions) == total_probes  # stopped by the policy, not the budget
    # On the real recorded profile (ADR-0023) BOTH families' leads get through, so the
    # agent exhausts the whole space (latent first by tie-break, then promptinject) and
    # abandons nothing — the "promptinject blocked" characterization was drift the live
    # run corrected. (The abandon-a-blocked-family behaviour is covered by the synthetic
    # §2 agency tests in test_red_team_agent.py.)
    assert set(trace.probe_sequence) == {
        p for fam in PROBE_CATALOG.values() for p in fam
    }
    assert trace.exploited_family == "latentinjection"
    assert trace.abandoned_families == ()


# --- 3. §2 agency preserved (now over live-capable observations) --------------


def test_agency_preserved_sequence_flips_with_observed_outcomes() -> None:
    # MA-00's honesty test, over the live entry: flip which family gets through and the
    # agent's exploitation target flips — the sequence is a function of observed outcomes.
    normal = live_red_team(observe=_profile_observe)
    flipped = live_red_team(observe=_flipped_observe)
    assert normal.exploited_family == "latentinjection"
    assert flipped.exploited_family == "promptinject"
    assert normal.probe_sequence != flipped.probe_sequence


# --- 4. the offline default is UNCHANGED (front door works with no Garak) ------


def test_build_red_team_view_offline_is_recorded_and_needs_no_garak() -> None:
    view = build_red_team_view()
    assert view.source == RECORDED_PROFILE_SOURCE
    assert "not an LLM" in view.mechanism
    assert view.probes_run > 0


def test_build_run_result_offline_tags_recorded_profile() -> None:
    # The whole offline arc: the red_team block is a recorded-profile run (no Garak).
    result = build_run_result()
    assert result.red_team.source == RECORDED_PROFILE_SOURCE


def test_build_red_team_view_live_with_fake_observe_tags_garak_live() -> None:
    view = build_red_team_view(live=True, observe=_profile_observe)
    assert view.source == GARAK_LIVE_SOURCE
    assert "REAL Garak scans" in view.mechanism


def test_build_red_team_view_live_falls_back_when_garak_down() -> None:
    view = build_red_team_view(live=True, observe=_unavailable_observe)
    assert view.source == RECORDED_PROFILE_SOURCE


# --- 5. scan scoping: tractable-default vs --deep (OPT-A-02b) ------------------


def test_deep_probes_are_classified_from_the_real_timings() -> None:
    # The deep set is the *Full variants + LatentWhois — the monsters the real OPT-A-02
    # scan measured (LatentWhois 168 prompts/~1550s, *Full e.g. 270 prompts/~955s+).
    assert "latentinjection.LatentWhois" in DEEP_PROBES
    assert all(
        is_deep(p) for fam in PROBE_CATALOG.values() for p in fam if p.endswith("Full")
    )
    # The shallow LatentWhoisSnippet (12 prompts) is NOT deep — only the real monsters are.
    assert not is_deep("latentinjection.LatentWhoisSnippet")
    # The tractable catalog is exactly the full catalog minus the deep probes.
    tractable = {p for fam in tractable_catalog().values() for p in fam}
    every = {p for fam in PROBE_CATALOG.values() for p in fam}
    assert tractable == every - set(DEEP_PROBES)
    assert tractable  # non-empty: there are real, cheap probes to scan


def test_default_live_scan_is_tractable_never_fires_a_deep_probe() -> None:
    # THE fix: the DEFAULT live red-team scans only the tractable set — no monster probe
    # is ever selected, so a real scan is bounded to minutes, not hours.
    trace = live_red_team(observe=_profile_observe)  # default scope
    assert trace.scan_scope == SCOPE_TRACTABLE
    assert not any(is_deep(p) for p in trace.probe_sequence)
    assert "latentinjection.LatentWhois" not in trace.probe_sequence


def test_deep_scope_includes_the_intractable_probes() -> None:
    # The opt-in --deep run exercises the FULL space, so the deep probes ARE selected
    # (the recorded profile has latent getting through, so the agent escalates into them).
    trace = live_red_team(observe=_profile_observe, scope=SCOPE_FULL)
    assert trace.scan_scope == SCOPE_FULL
    assert any(is_deep(p) for p in trace.probe_sequence)


def test_build_red_team_view_live_default_is_tractable() -> None:
    view = build_red_team_view(live=True, observe=_profile_observe)
    assert view.scan_scope == SCOPE_TRACTABLE
    assert not any(is_deep(p) for p in view.probe_sequence)


def test_build_red_team_view_deep_scans_the_full_set() -> None:
    view = build_red_team_view(live=True, deep=True, observe=_profile_observe)
    assert view.scan_scope == SCOPE_FULL
    assert any(is_deep(p) for p in view.probe_sequence)


def test_offline_recorded_run_is_full_scope() -> None:
    # The offline recorded run has the whole catalog selectable (no live cost) → "full".
    view = build_red_team_view()
    assert view.source == RECORDED_PROFILE_SOURCE
    assert view.scan_scope == SCOPE_FULL


def test_live_triage_does_not_trigger_the_red_team_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # THE OPT-A-01b pain fixed (OPT-A-02b): with ONLY triage live, the red-team stays on
    # the recorded profile — no Garak scan is launched. (Force triage offline via an
    # unreachable backend so the test needs no Ollama and no network.)
    class _DownBackend:
        model = "down"

        def complete(self, prompt: str, *, system: str | None = None) -> str:
            raise BackendUnreachableError("stubbed offline")

    # The package re-exports the `triage` function, shadowing the submodule attribute, so
    # reach the real module via sys.modules to patch the name live_triage looks up. Patch
    # to the class itself — `get_backend()` then constructs a fresh _DownBackend per call.
    monkeypatch.setattr(
        sys.modules["keystone.agents.triage"], "get_backend", _DownBackend
    )
    result = build_run_result(live=LiveModes(triage=True, redteam=False))
    # Red-team never scanned: recorded profile, full scope, offline.
    assert result.red_team.source == RECORDED_PROFILE_SOURCE
    assert result.red_team.scan_scope == SCOPE_FULL
    # Triage genuinely took the live path (then fell back offline) — not a live scan.
    assert result.triage.reasoner == "policy_fallback"


# --- 6. the ONE real-Garak check (slow; skips if Garak/Ollama unavailable) -----


def _ollama_up() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2.0)
    except httpx.HTTPError:
        return False
    return True


@pytest.mark.slow
def test_real_garak_live_run_tags_the_source_honestly() -> None:
    # A genuine live run (bounded budget for test tractability — the FULL untimed sequence
    # is the operational-profile proof reported in the PR). We do NOT assert WHICH probes
    # land — only that live mode is honest: real outcomes and the source tag matches what
    # ran (garak_live on success, recorded_profile if it fell back), never anything else.
    if shutil.which("garak") is None and shutil.which("uv") is None:
        pytest.skip("garak CLI not available")
    if not _ollama_up():
        pytest.skip("Ollama not running")
    trace = live_red_team(budget=2, report_prefix="opta02_test_live", prompt_cap=4)
    assert trace.source in {GARAK_LIVE_SOURCE, RECORDED_PROFILE_SOURCE}
    if trace.source == GARAK_LIVE_SOURCE:
        assert all(d.outcome.total_evaluated > 0 for d in trace.decisions)
