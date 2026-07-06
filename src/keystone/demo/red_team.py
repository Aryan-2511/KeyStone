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


def project_red_team_view(trace: RedTeamTrace) -> RedTeamView:
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


def red_team_trace(
    *, live: bool = False, deep: bool = False, observe: Observe | None = None
) -> RedTeamTrace:
    """Run the Red-Team Agent and return its RAW trace (before projection).

    Default (``live=False``): the agent observes the recorded defense profile and adapts —
    the trace replays deterministically (MA-00 §4). Opt-in (``live=True``, OPT-A-02): each
    probe is a real Garak scan (tractable unless ``deep``), with the recorded profile as a
    source-tagged fallback. Exposed so the runner can both project the view AND close the
    MC-02 adversarial loop over the same trace (no double run). ``observe`` injectable (tests).
    """
    if live:
        return live_red_team(
            observe=observe, scope=SCOPE_FULL if deep else SCOPE_TRACTABLE
        )
    return run_red_team(profile_observe(RECORDED_DEFENSE_PROFILE))


def build_red_team_view(
    *, live: bool = False, deep: bool = False, observe: Observe | None = None
) -> RedTeamView:
    """Run the Red-Team Agent and project its trace into the typed view.

    Thin wrapper over :func:`red_team_trace` + :func:`_project`; see that function for the
    live / recorded / scope semantics. The projected ``source`` / ``mechanism`` /
    ``scan_scope`` state what actually ran; a fallback is never reported as a live scan.
    """
    return project_red_team_view(red_team_trace(live=live, deep=deep, observe=observe))
