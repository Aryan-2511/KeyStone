"""Run the FROZEN held-out eval against whatever Ollama model is configured.

The SAME harness measures both sides of the decisive comparison — just point it at a
different model via the environment:

    # general-3B baseline (the number to beat: OPT-A-01b held-out was 4/6):
    uv run python scripts/finetune_eval.py

    # the fine-tuned adapter, served on-prem under its own Ollama name:
    KEYSTONE_OLLAMA_MODEL=keystone-triage-ft uv run python scripts/finetune_eval.py

Each held-out case is routed by the live LLM (via :func:`keystone.agents.triage.live_triage`,
same signal-only prompt, policy as fallback) ``--repeats`` times; the majority route is compared
to the frozen policy label. Reports overall accuracy, **reserved-band accuracy** (the axis general
3B failed on), per-route accuracy, and the fallback count. It is a REPORT, not a pass/fail gate.

If Ollama is unavailable every case falls back to the policy — the harness still runs and simply
reports that the LLM added nothing (honest degradation); the baseline must be captured with Ollama
serving the model under test.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from keystone.agents.triage import TriageSignals, live_triage
from keystone.finetune.protocol import Case, read_cases_jsonl
from keystone.llm.inference import get_backend

HELDOUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "keystone"
    / "finetune"
    / "data"
    / "heldout_eval.jsonl"
)


def _signal_str(s: TriageSignals) -> str:
    return (
        f"rate={s.failure_rate:.2f} seam={s.seam_result.value} sev={s.severity.value}"
    )


def _llm_route(signals: TriageSignals, repeats: int) -> tuple[str, bool]:
    """Majority LLM route over ``repeats`` calls, plus whether it ever fell back."""
    routes: Counter[str] = Counter()
    fell_back = False
    for _ in range(repeats):
        decision = live_triage(signals)
        if decision.reasoner.startswith("llm:"):
            routes[decision.route.value] += 1
        else:
            fell_back = True
            routes["policy_fallback"] += 1
    top, _ = routes.most_common(1)[0]
    return top, fell_back


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repeats", type=int, default=3, help="LLM calls per case (default 3)"
    )
    parser.add_argument("--verbose", action="store_true", help="print every case")
    args = parser.parse_args()

    model = getattr(get_backend(), "model", "unknown")
    cases: list[Case] = read_cases_jsonl(HELDOUT_PATH)

    print(f"Frozen held-out eval ({len(cases)} cases) vs model: {model}")
    print(f"{args.repeats} LLM call(s) per case; the policy label is the ground truth.")
    print("=" * 78)

    correct = band_correct = band_total = fallbacks = 0
    per_route_ok: Counter[str] = Counter()
    per_route_total: Counter[str] = Counter()
    for case in cases:
        expected = case.route.value
        got, fell_back = _llm_route(case.signals, args.repeats)
        ok = got == expected
        correct += int(ok)
        fallbacks += int(fell_back)
        per_route_total[expected] += 1
        per_route_ok[expected] += int(ok)
        if case.in_band:
            band_total += 1
            band_correct += int(ok)
        if args.verbose:
            mark = "ok " if ok else "XX "
            print(
                f"{mark}[{case.name}] {_signal_str(case.signals)} -> got {got}, want {expected}"
            )

    print("-" * 78)
    print(
        f"Overall held-out accuracy : {correct}/{len(cases)} = {correct / len(cases):.0%}"
    )
    if band_total:
        print(
            f"Reserved-band accuracy    : {band_correct}/{band_total} = "
            f"{band_correct / band_total:.0%}  (the 0.10-threshold axis general 3B failed on)"
        )
    for route in sorted(per_route_total):
        tot = per_route_total[route]
        print(
            f"  route {route:<9}: {per_route_ok[route]}/{tot} = {per_route_ok[route] / tot:.0%}"
        )
    if fallbacks:
        print(
            f"NOTE: {fallbacks} case(s) fell back to the policy (LLM unavailable/unparseable)."
        )
    print(
        "\nHonest read: the decisive comparison is THIS model's held-out accuracy vs the "
        "general-3B baseline. Higher = specialization closed the gap; equal = capacity-bound."
    )
    return 0  # a report, never a gate


if __name__ == "__main__":
    raise SystemExit(main())
