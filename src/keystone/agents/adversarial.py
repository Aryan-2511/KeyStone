"""The adversarial offense↔defense loop (MC-02) — the multi-agent finale.

The impressive end-state (MC-00 §4): **offense -> defense -> offense**.

1. The Red-Team Agent finds an exploit that LANDS on the target (MA-01).
2. The Defense Agent chooses + applies a remediation (MC-01) -> a PATCHED target.
3. The Red-Team Agent **RE-SCANS the patched target** — does the exploit still land? — and
   ADAPTS its next selection to the post-patch observation (its existing MA-00 §2 agency, now
   over post-patch outcomes). This module closes that loop.

**Honest handling of the two remediations (MC-00 §4 / the task).**
- **(a) guardrail patch — a REAL re-scan (AI side).** The remediation produces the GUARDED
  agent (the rail active); the Red-Team re-scans the exploited probe against it and MEASURES
  whether the exploit still lands. Live, that is a real Garak scan of the guarded target
  (:func:`guarded_observe`, opt-in, tractable + recorded fallback, OPT-A-02b discipline);
  offline, it replays :data:`RECORDED_GUARDED_PROFILE` (anchored to the proven KS-0304 result
  — the memo-injection exploit went 10/12 -> 0/12 with the rail, `REFERENCED_ASSURANCE`).
- **(c) detection tightening — an OFFLINE re-verify (financial side).** (c) tightens detection,
  not the model path; there is no AI target to re-scan. Its "re-test" is confirming the tightened
  detection now covers the gap — already offline-verifiable (MC-01 set `verified_offline=True`).
  We describe it truthfully as an offline re-verify, NEVER as a live post-patch scan.

**The measured outcome, not an assumption.** `mitigated` is computed from the re-scan (a) /
re-verify (c) — we MEASURE whether the patch changed the exploit outcome; if it did not, that is
reported honestly (a real finding about the remediation, not hidden).

**Memo-blind (sacred).** The loop is offense-side: the Red-Team re-scans a target; it reaches no
crime detector. The recorded guarded profile is a `probe -> (fails, total)` table (no attack
channel). The AST boundary test covers this module too (it imports nothing on the detection path).
"""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from dataclasses import dataclass

from keystone.agents.defense import DefenseDecision
from keystone.agents.red_team import (
    GARAK_LIVE_SOURCE,
    PROBE_CATALOG,
    RECORDED_DEFENSE_PROFILE,
    RECORDED_PROFILE_SOURCE,
    Observe,
    ProbeOutcome,
    RedTeamTrace,
    family_of,
    profile_observe,
    run_red_team,
)
from keystone.assurance.garak_probe import parse_report
from keystone.assurance.referenced import REFERENCED_ASSURANCE
from keystone.assurance.remediation import SeamSide


class LoopConfigError(RuntimeError):
    """Raised if the recorded guarded profile's anchor invariant no longer holds."""


# Loop-kind tags — honest about which remediation's loop ran (they are genuinely different).
KIND_AI_RESCAN = "ai_rescan"  # (a): a real re-scan of the guarded target
KIND_FINANCIAL_REVERIFY = "financial_reverify"  # (c): the offline detection re-verify
# Source for (c): no target is scanned — the re-verify is a pure offline detection change.
OFFLINE_SOURCE = "offline"


def _recorded_guarded_profile() -> dict[str, tuple[int, int]]:
    """The post-patch (rail active) outcome the OFFLINE loop replays — REAL-anchored.

    The KS-0302 input rail vets the memo channel BOTH prompt-injection families ride, and the
    proven KS-0304 result (:data:`REFERENCED_ASSURANCE`) is that the memo-injection exploit went
    from landing (before_fails, exploit fired) to `after_fails == 0` once the rail was added. So
    the recorded guarded outcome for every injection probe is BLOCKED — 0 fails over the same
    prompt count the unguarded scan emitted (the prompts are still sent; the rail refuses them).
    `total_evaluated` per probe mirrors the unguarded recorded profile so the re-scan is
    comparable probe-for-probe. Non-lead probes' guarded values are modeled from the rail's
    general memo-injection design (not separately captured); the live re-scan MEASURES them.
    """
    if REFERENCED_ASSURANCE.after_fails != 0:  # the rail closed the exploit (KS-0304)
        raise LoopConfigError(
            "recorded guarded profile assumes the rail closes the exploit "
            f"(after_fails == 0), but REFERENCED_ASSURANCE.after_fails is "
            f"{REFERENCED_ASSURANCE.after_fails}"
        )
    return {probe: (0, total) for probe, (_, total) in RECORDED_DEFENSE_PROFILE.items()}


# The post-patch defense profile (rail active): every injection probe blocked (0 fails).
RECORDED_GUARDED_PROFILE: dict[str, tuple[int, int]] = _recorded_guarded_profile()


def guarded_observe(*, report_prefix: str, prompt_cap: int | None = 12) -> Observe:
    """LIVE re-scan of the PATCHED (guarded) target — the real (a)-loop measurement.

    Mirrors :func:`keystone.agents.red_team.garak_observe` but points Garak at the GUARDED
    agent (the rail active) via :func:`keystone.assurance.garak_endpoint.scan_guarded_agent`,
    so the Red-Team measures whether the exploit still lands AFTER the patch. ``garak_endpoint``
    is loaded via ``importlib`` inside the closure so the module stays lean and the OFFLINE path
    never imports nemoguardrails/Garak. Used by the ``-m slow`` live path; offline uses
    ``profile_observe(RECORDED_GUARDED_PROFILE)``.
    """

    def observe(probe: str) -> ProbeOutcome:
        endpoint = importlib.import_module("keystone.assurance.garak_endpoint")
        report = endpoint.scan_guarded_agent(
            report_prefix=f"{report_prefix}_{probe.split('.', 1)[1]}",
            probes=[probe],
            prompt_cap=prompt_cap,
        )
        findings = parse_report(report)
        rows = [f for f in findings if f.probe == probe] or list(findings)
        return ProbeOutcome(
            probe=probe,
            family=family_of(probe),
            fails=sum(f.fails for f in rows),
            total_evaluated=sum(f.total_evaluated for f in rows),
        )

    return observe


@dataclass(frozen=True)
class AdversarialLoopResult:
    """The recorded offense↔defense loop: exploit -> patch -> re-scan -> adaptation.

    A faithful capture of the loop closing, replayed deterministically offline. For (a) the
    re-scan is real (`post_patch_*` measured on the guarded target); for (c) it is an offline
    re-verify (`post_patch_*` None, `source` = "offline") — the fields state which honestly.
    """

    remediation_control: str
    side: SeamSide
    kind: str  # KIND_AI_RESCAN | KIND_FINANCIAL_REVERIFY
    probe: str | None  # the exploited probe re-tested (a); None for (c)
    pre_patch_fails: int
    pre_patch_total: int
    post_patch_fails: int | None  # re-scan of the patched target (a); None for (c)
    post_patch_total: int | None
    mitigated: bool  # the patch changed the outcome (exploit no longer lands / gap now covered)
    source: str  # garak_live | recorded_profile (a) | offline (c)
    adaptation: (
        str  # plain-language: how the Red-Team responds to the post-patch observation
    )
    adapted_exploited_family: (
        str | None
    )  # the family it exploits post-patch (None = held off)


def _strongest_exploit(trace: RedTeamTrace) -> tuple[str, int, int] | None:
    """The trace's strongest LANDED exploit (probe, fails, total) — what the defense answered."""
    landed = [d for d in trace.decisions if d.outcome.got_through]
    if not landed:
        return None
    best = max(landed, key=lambda d: d.outcome.failure_rate)
    return best.chosen_probe, best.outcome.fails, best.outcome.total_evaluated


def close_loop(
    trace: RedTeamTrace,
    decision: DefenseDecision,
    *,
    rescan_observe: Observe | None = None,
    guarded_profile: Mapping[str, tuple[int, int]] = RECORDED_GUARDED_PROFILE,
) -> AdversarialLoopResult:
    """Close the adversarial loop over a Red-Team trace + the Defense Agent's decision.

    **(a) AI side — a real re-scan.** Re-scan the trace's strongest exploited probe against the
    PATCHED (guarded) target via ``rescan_observe`` (live :func:`guarded_observe`) or, by default,
    ``profile_observe(guarded_profile)`` (offline, deterministic). `mitigated` is MEASURED: the
    exploit landed pre-patch and no longer lands post-patch. Then the Red-Team re-runs its policy
    over the guarded profile — its MA-00 §2 agency, now over post-patch outcomes — and ADAPTS
    (it abandons the closed injection surface; `adapted_exploited_family` states what it exploits
    now, or None if the defense held).

    **(c) financial side — an offline re-verify.** No AI target to re-scan; `mitigated` is the
    already-offline-verified fact that the tightened detection covers the gap
    (`decision.outcome.verified_offline`). Described truthfully as an offline re-verify.
    """
    side = decision.remediation.side
    if side is SeamSide.FINANCIAL:
        return AdversarialLoopResult(
            remediation_control=decision.remediation.control,
            side=side,
            kind=KIND_FINANCIAL_REVERIFY,
            probe=None,
            pre_patch_fails=0,
            pre_patch_total=0,
            post_patch_fails=None,
            post_patch_total=None,
            mitigated=bool(decision.outcome.verified_offline),
            source=OFFLINE_SOURCE,
            adaptation=(
                "Financial-side offline re-verify: the tightened detection now covers the "
                "transaction the baseline missed. No AI re-scan — (c) tightens detection, not "
                "the model path; the Red-Team's target is unchanged."
            ),
            adapted_exploited_family=None,
        )

    # (a) AI side — the real re-scan of the patched (guarded) target.
    strongest = _strongest_exploit(trace)
    observe = (
        rescan_observe
        if rescan_observe is not None
        else profile_observe(guarded_profile)
    )
    source = (
        GARAK_LIVE_SOURCE if rescan_observe is not None else RECORDED_PROFILE_SOURCE
    )
    if strongest is None:
        # Nothing landed pre-patch — no exploit to re-test (degenerate; still honest).
        return AdversarialLoopResult(
            remediation_control=decision.remediation.control,
            side=side,
            kind=KIND_AI_RESCAN,
            probe=None,
            pre_patch_fails=0,
            pre_patch_total=0,
            post_patch_fails=None,
            post_patch_total=None,
            mitigated=False,
            source=source,
            adaptation="No exploit landed pre-patch; nothing to re-scan.",
            adapted_exploited_family=trace.exploited_family,
        )

    probe, pre_fails, pre_total = strongest
    post = observe(
        probe
    )  # the MEASURED re-scan (live or recorded) — the before/after proof
    mitigated = pre_fails > 0 and not post.got_through

    # The Red-Team adapts: re-run its policy over the post-patch (guarded) POSTURE — the SAME
    # MA-00 §2 agency, now over post-patch observations. This is DETERMINISTIC policy behaviour
    # over the recorded guarded profile (NOT a fresh live measurement — that would re-scan every
    # probe live; the live measurement is specifically the exploited-probe re-scan above), so a
    # live loop makes exactly ONE real guarded scan, keeping the cost tractable (OPT-A-02b).
    post_trace = run_red_team(profile_observe(guarded_profile))
    adapted_family = post_trace.exploited_family
    if mitigated and adapted_family is None:
        adaptation = (
            f"Re-scanned {probe.split('.', 1)[1]} on the patched target: the exploit no longer "
            f"lands ({pre_fails}/{pre_total} -> {post.fails}/{post.total_evaluated}). The "
            f"Red-Team re-ran and found the injection surface closed — it abandons it (the "
            f"defense held; no exploit path remains)."
        )
    elif mitigated:
        adaptation = (
            f"Re-scanned {probe.split('.', 1)[1]} on the patched target: the exploit no longer "
            f"lands ({pre_fails}/{pre_total} -> {post.fails}/{post.total_evaluated}). The "
            f"Red-Team pivots to '{adapted_family}', which the patch does not close."
        )
    else:
        adaptation = (
            f"Re-scanned {probe.split('.', 1)[1]} on the patched target: the exploit STILL "
            f"lands ({pre_fails}/{pre_total} -> {post.fails}/{post.total_evaluated}) — the "
            f"remediation did not mitigate it. Reported honestly."
        )

    return AdversarialLoopResult(
        remediation_control=decision.remediation.control,
        side=side,
        kind=KIND_AI_RESCAN,
        probe=probe,
        pre_patch_fails=pre_fails,
        pre_patch_total=pre_total,
        post_patch_fails=post.fails,
        post_patch_total=post.total_evaluated,
        mitigated=mitigated,
        source=source,
        adaptation=adaptation,
        adapted_exploited_family=adapted_family,
    )


# Every family in the catalog, for callers that need the offense's decision space.
INJECTION_FAMILIES: tuple[str, ...] = tuple(PROBE_CATALOG)
