"""Honest LLM-vs-policy evaluation for the live Triage Agent (OPT-A-01, OPT-A-00 §5).

Runs a set of (failure_rate, seam_result, severity) scenarios - including the real arc
finding's signals - through BOTH reasoners side by side:

  * the transparent **policy** (deterministic, the fallback), and
  * the **live LLM** (qwen2.5:3b via Ollama), called several times per scenario so its
    run-to-run consistency is visible (the deferred 3B-reliability question, answered
    empirically).

It prints, per scenario: the policy route, the LLM's route distribution over the repeats,
whether they AGREE, and a sample LLM rationale - then a summary of agreements /
disagreements / fallbacks. It does NOT assume the LLM wins: the honest deliverable is
"here is what live reasoning actually does vs the policy," not a pass/fail gate.

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


def _signal_str(s: TriageSignals) -> str:
    return (
        f"rate={s.failure_rate:.2f} seam={s.seam_result.value} sev={s.severity.value}"
    )


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

    print("Live Triage Agent - LLM vs policy (OPT-A-01)")
    print("=" * 78)
    print(f"{repeats} LLM call(s) per scenario; the policy is deterministic.\n")

    agreements = 0
    disagreements = 0
    fallbacks = 0

    for name, signals in SCENARIOS:
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
                fallbacks += 1

        # The LLM's most common route this scenario (its "answer"), agreement vs policy.
        top_route, _ = llm_routes.most_common(1)[0]
        agrees = top_route == policy_route.value
        if top_route == "policy_fallback":
            verdict = "FELL BACK"
        elif agrees:
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

    print("-" * 78)
    print(
        f"Summary: {agreements} agree, {disagreements} differ, "
        f"{fallbacks} fallback call(s) of {repeats * len(SCENARIOS)} total LLM calls."
    )
    print(
        "Read this honestly: agreement is not proof the LLM is 'right', and a difference "
        "is not proof it is 'better' - it is what live 3B reasoning actually does here."
    )
    # Not a gate: always exit 0. The evaluation is a report, not a pass/fail check.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
