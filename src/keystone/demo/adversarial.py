"""Build the closed adversarial loop's recorded view from a genuine run (MC-02).

The `adversarial_loop` block of the `RunResult` is DERIVED by actually running the loop
(`keystone.agents.adversarial.close_loop`) over the Red-Team's trace and the Defense Agent's
decision: it re-scans the PATCHED target and records whether the exploit still lands, plus the
Red-Team's adaptation. Offline (default) the re-scan replays the recorded guarded profile
(deterministic); live (opt-in) it runs a real Garak re-scan of the guarded target, with the
recorded profile as a source-tagged fallback — the OPT-A-02b cost discipline.

Boundary: lives in `keystone.demo`; the core never imports it. The loop is offense-side and
reaches no crime detector (memo-blind holds).
"""

from __future__ import annotations

from keystone.agents.adversarial import (
    AdversarialLoopResult,
    close_loop,
    guarded_observe,
)
from keystone.agents.defense import DefenseDecision
from keystone.agents.red_team import RedTeamTrace
from keystone.assurance.garak_probe import GarakError

from .run_result import AdversarialLoopView


def _project(result: AdversarialLoopResult) -> AdversarialLoopView:
    return AdversarialLoopView(
        remediation_control=result.remediation_control,
        side=result.side.value,
        kind=result.kind,
        probe=result.probe,
        pre_patch_fails=result.pre_patch_fails,
        pre_patch_total=result.pre_patch_total,
        post_patch_fails=result.post_patch_fails,
        post_patch_total=result.post_patch_total,
        mitigated=result.mitigated,
        source=result.source,
        adaptation=result.adaptation,
        adapted_exploited_family=result.adapted_exploited_family,
    )


def build_adversarial_loop_view(
    *,
    trace: RedTeamTrace,
    decision: DefenseDecision,
    live: bool = False,
    report_prefix: str = "keystone_mc02_rescan",
) -> AdversarialLoopView:
    """Close the loop over the Red-Team trace + Defense decision and project it.

    Default (``live=False``): the re-scan replays the recorded guarded profile — deterministic,
    no Garak/Ollama. Opt-in (``live=True``): the (a) AI-side re-scan is a REAL Garak scan of the
    guarded target (:func:`keystone.agents.adversarial.guarded_observe`); on any Garak failure it
    falls back to the recorded guarded profile — the loop is ALWAYS produced, the source honestly
    tagged (a fallback is never reported as a live scan). ``live`` only affects the (a) re-scan;
    (c)'s loop is an offline re-verify regardless.
    """
    if live:
        try:
            result = close_loop(
                trace,
                decision,
                rescan_observe=guarded_observe(report_prefix=report_prefix),
            )
        except GarakError:
            # Garak unavailable / target down / scan errored → the recorded guarded profile
            # produces a complete, valid loop, honestly tagged as the fallback source.
            result = close_loop(trace, decision)
    else:
        result = close_loop(trace, decision)
    return _project(result)
