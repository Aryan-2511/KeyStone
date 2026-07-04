"""Build the Red-Team Agent's recorded decision trace from a genuine run (MA-01).

The `red_team` block of the `RunResult` is DERIVED by actually RUNNING the agent
(`keystone.agents.red_team.run_red_team`) over the recorded, deterministic defense
profile — never hand-authored. Offline, the agent observes via the recorded profile
(`RECORDED_DEFENSE_PROFILE`) so the genuine adaptive run replays identically with no
network/GPU (MA-00 §4); live, the same agent would observe via real Garak scans.
This module holds only the presentation derivation: projecting the agent's trace
into the typed view the front-end renders.

Boundary: lives in `keystone.demo` (the integration layer) and draws on the
`keystone.agents` edge; the core never imports it (import-linter KEPT). The agent it
runs is OFFENSE-only and has no path to the memo-blind detector (MA-00 §5).
"""

from __future__ import annotations

from keystone.agents.red_team import (
    PROBE_CATALOG,
    RECORDED_DEFENSE_PROFILE,
    SCOPE_FULL,
    SCOPE_TRACTABLE,
    Observe,
    RedTeamTrace,
    live_red_team,
    mechanism_for,
    profile_observe,
    run_red_team,
)

from .run_result import RedTeamProbeView, RedTeamView


def _project(trace: RedTeamTrace) -> RedTeamView:
    """Project a genuine agent trace into the typed view (reading its DERIVED steps)."""
    decisions = tuple(
        RedTeamProbeView(
            step=d.step,
            phase=d.phase,
            family=d.chosen_family,
            probe=d.chosen_probe,
            rationale=d.rationale,
            fails=d.outcome.fails,
            total_evaluated=d.outcome.total_evaluated,
            failure_rate=d.outcome.failure_rate,
            got_through=d.outcome.got_through,
        )
        for d in trace.decisions
    )
    return RedTeamView(
        decisions=decisions,
        probe_sequence=trace.probe_sequence,
        families_available=tuple(PROBE_CATALOG),
        scouted_families=trace.scouted_families,
        exploited_family=trace.exploited_family,
        abandoned_families=trace.abandoned_families,
        probes_run=len(trace.decisions),
        mechanism=mechanism_for(trace.source),
        source=trace.source,
        scan_scope=trace.scan_scope,
    )


def build_red_team_view(
    *, live: bool = False, deep: bool = False, observe: Observe | None = None
) -> RedTeamView:
    """Run the Red-Team Agent and project its trace into the typed view.

    Default (``live=False``): the agent observes the recorded defense profile, reasons
    via its policy, and adapts — the trace replays deterministically (MA-00 §4), tagged
    ``recorded_profile`` / scope ``full`` (the whole catalog is selectable; no live cost).
    Opt-in (``live=True``, OPT-A-02): the SAME policy selects probes but each is EXECUTED
    as a real Garak scan, with the recorded profile as a proven fallback; the trace is
    tagged ``garak_live`` or — on any Garak failure — ``recorded_profile``.

    ``deep`` bounds the live scan (OPT-A-02b, the intractable-probe fix): the default live
    run scans only the TRACTABLE set (``scope=tractable`` — minutes, never a monster probe);
    ``deep=True`` runs the FULL set incl. the known-intractable deep probes (hours). The
    projected ``source``/``mechanism``/``scan_scope`` state what actually ran; a fallback
    is never reported as a live scan (OPT-A-02 §3). ``observe`` is injectable (tests).
    """
    if live:
        trace = live_red_team(
            observe=observe, scope=SCOPE_FULL if deep else SCOPE_TRACTABLE
        )
    else:
        trace = run_red_team(profile_observe(RECORDED_DEFENSE_PROFILE))
    return _project(trace)
