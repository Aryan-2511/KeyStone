"""Honest LLM-vs-policy evaluation for the live Triage Agent (OPT-A-01 / OPT-A-01b).

Runs (failure_rate, seam_result, severity) scenarios through BOTH reasoners side by side:

  * the transparent **policy** (deterministic ground truth, also the fallback), and
  * the **live LLM** (qwen2.5:3b via Ollama), called several times per scenario so its
    run-to-run consistency is visible (the deferred 3B-reliability question, answered
    empirically).

Two blocks, because OPT-A-01b (the prompt-rescue) asks a sharper question than OPT-A-01:

  1. **In-distribution** (:data:`SCENARIOS`) - the real arc finding + the MB-01 interplay
     set. This is the SAME set OPT-A-01 measured, kept identical for a fair before/after.
  2. **Held-out** (:data:`HELDOUT_SCENARIOS`) - (seam, severity) combos and rates the
     prompt's few-shot examples NEVER show, each built so a model that PARROTS the
     examples ("seam -> route") gets it WRONG while one that applies the override RULES
     gets it right. This separates genuine rule-application from few-shot pattern-match:
     strong in-distribution accuracy is only meaningful if it survives held-out probes.

It prints, per scenario: the policy route, the LLM's route distribution over the repeats,
whether they AGREE, and a sample LLM rationale - then a per-block summary. It does NOT
assume the LLM wins: the honest deliverable is "here is what live reasoning actually does
vs the policy, in AND out of distribution," not a pass/fail gate.

The prompt carries the SIGNALS only - never the attack channel (the boundary is sacred).

Run:  uv run python scripts/triage_llm_eval.py            (needs Ollama up)
      uv run python scripts/triage_llm_eval.py --repeats 5
If Ollama is unavailable every scenario reports policy_fallback - the script still runs
(honest degradation), it just shows the LLM added nothing this time.
"""

from __future__ import annotations

import argparse
from collections import Counter

from keystone.agents.triage import (
    FindingSeverity,
    SeamClassification,
    TriageSignals,
    live_triage,
    route_for,
)

# The scenarios: the real arc finding first, then the MB-01 interplay set (same rate,
# different seam - the "not a single threshold" probe) and the policy's boundary cells.
SCENARIOS: tuple[tuple[str, TriageSignals], ...] = (
    (
        "real arc finding",
        TriageSignals(
            failure_rate=0.83,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.HIGH,
        ),
    ),
    (
        "interplay: clean",
        TriageSignals(
            failure_rate=0.50,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.MEDIUM,
        ),
    ),
    (
        "interplay: boundary",
        TriageSignals(
            failure_rate=0.50,
            seam_result=SeamClassification.BOUNDARY,
            severity=FindingSeverity.MEDIUM,
        ),
    ),
    (
        "interplay: open",
        TriageSignals(
            failure_rate=0.50,
            seam_result=SeamClassification.OPEN,
            severity=FindingSeverity.MEDIUM,
        ),
    ),
    (
        "below floor",
        TriageSignals(
            failure_rate=0.02,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.LOW,
        ),
    ),
    (
        "open, moderate",
        TriageSignals(
            failure_rate=0.40,
            seam_result=SeamClassification.OPEN,
            severity=FindingSeverity.LOW,
        ),
    ),
)


# Held-out anti-parrot probe (OPT-A-01b): (seam, severity) combos and rates the prompt's
# few-shot examples never show, each chosen so PARROTING the examples yields the WRONG
# route while applying the override RULES yields the right one. The comments name the
# discriminator - what a pattern-matcher gets wrong here.
HELDOUT_SCENARIOS: tuple[tuple[str, TriageSignals], ...] = (
    (
        "clean HIGH: HIGH overrides clean-remediate",  # parrot(clean->remediate) fails
        TriageSignals(
            failure_rate=0.12,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.HIGH,
        ),
    ),
    (
        "clean LOW above floor -> remediate",  # only clean+LOW example was 0.05->accept
        TriageSignals(
            failure_rate=0.25,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.LOW,
        ),
    ),
    (
        "open MED below floor -> accept",  # floor beats open->escalate; must read 0.06<0.10
        TriageSignals(
            failure_rate=0.06,
            seam_result=SeamClassification.OPEN,
            severity=FindingSeverity.MEDIUM,
        ),
    ),
    (
        "boundary HIGH below floor -> escalate",  # HIGH overrides floor+boundary
        TriageSignals(
            failure_rate=0.08,
            seam_result=SeamClassification.BOUNDARY,
            severity=FindingSeverity.HIGH,
        ),
    ),
    (
        "boundary LOW (unshown combo) -> accept",
        TriageSignals(
            failure_rate=0.30,
            seam_result=SeamClassification.BOUNDARY,
            severity=FindingSeverity.LOW,
        ),
    ),
    (
        "open HIGH mid-rate -> escalate (no collapse)",
        TriageSignals(
            failure_rate=0.45,
            seam_result=SeamClassification.OPEN,
            severity=FindingSeverity.HIGH,
        ),
    ),
)


def _signal_str(s: TriageSignals) -> str:
    return (
        f"rate={s.failure_rate:.2f} seam={s.seam_result.value} sev={s.severity.value}"
    )


def _run_block(
    title: str, scenarios: tuple[tuple[str, TriageSignals], ...], repeats: int
) -> tuple[int, int, int]:
    """Run one scenario block, print it, return (agree, differ, fallback) scenario counts."""
    print(title)
    print("=" * 78)
    print(f"{repeats} LLM call(s) per scenario; the policy is deterministic.\n")

    agreements = disagreements = fallbacks = 0
    for name, signals in scenarios:
        policy_route = route_for(signals)
        llm_routes: Counter[str] = Counter()
        sample_rationale = ""
        for _ in range(repeats):
            decision = live_triage(signals)
            if decision.reasoner.startswith("llm:"):
                llm_routes[decision.route.value] += 1
                if not sample_rationale:
                    sample_rationale = decision.rationale
            else:
                llm_routes["policy_fallback"] += 1

        # The LLM's most common route this scenario (its "answer"), agreement vs policy.
        top_route, _ = llm_routes.most_common(1)[0]
        if top_route == "policy_fallback":
            verdict = "FELL BACK"
            fallbacks += 1
        elif top_route == policy_route.value:
            verdict = "agree"
            agreements += 1
        else:
            verdict = "DIFFER"
            disagreements += 1

        dist = ", ".join(f"{r}x{c}" for r, c in llm_routes.most_common())
        print(f"[{name}]  {_signal_str(signals)}")
        print(f"   policy : {policy_route.value}")
        print(f"   llm    : {dist}   -> {verdict}")
        if sample_rationale:
            print(f"   why    : {sample_rationale}")
        print()
    return agreements, disagreements, fallbacks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repeats",
        type=int,
        default=3,
        help="how many times to call the LLM per scenario (default 3)",
    )
    args = parser.parse_args()
    repeats: int = args.repeats

    in_dist = _run_block(
        "Live Triage Agent - LLM vs policy: IN-DISTRIBUTION (OPT-A-01 set)",
        SCENARIOS,
        repeats,
    )
    print()
    held = _run_block(
        "Live Triage Agent - LLM vs policy: HELD-OUT anti-parrot probe (OPT-A-01b)",
        HELDOUT_SCENARIOS,
        repeats,
    )

    print("-" * 78)
    print(
        f"In-distribution : {in_dist[0]}/{len(SCENARIOS)} agree, "
        f"{in_dist[1]} differ, {in_dist[2]} fell back."
    )
    print(
        f"Held-out        : {held[0]}/{len(HELDOUT_SCENARIOS)} agree, "
        f"{held[1]} differ, {held[2]} fell back."
    )
    print(
        "Read this honestly: strong IN-distribution agreement that DROPS on the held-out "
        "probe is few-shot pattern-matching, not robust rule-application - which is exactly "
        "what OPT-A-01b found (great on the example-shaped set, worse on novel combos)."
    )
    # Not a gate: always exit 0. The evaluation is a report, not a pass/fail check.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
