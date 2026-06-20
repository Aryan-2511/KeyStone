"""The Layer-2 AI Assurance Loop (KS-0304) — compose the existing pieces.

This builds NO new capability: it sequences the KS-0301 agent, the KS-0303 Garak
detector + mapping, and the KS-0302 Guardrails patch into one end-to-end arc and
records it to the evidence ledger:

    EXPOSED → DETECTED → MAPPED → PATCHED → VERIFIED (-closed)

`run_assurance_loop` is the deterministic spine: it runs the five stages in order,
each writing one `assurance_loop_stage` ledger entry, and is dependency-injected
(`LoopDeps`) so the fast gate exercises the exact same sequencing over canned
results — no Garak, no Ollama. `live_deps()` wires the real components for the
NAT-orchestrated milestone. `assert_assurance_arc` is the milestone check: the
ledger must hold the full ordered arc and hash-verify.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from keystone.core.ledger import Ledger, open_ledger

from .agent import AgentRun, exploit_fired
from .garak_probe import (
    PROMPT_INJECTION_FAMILIES,
    GarakFinding,
    found_our_vulnerability,
    map_finding,
)

LOOP_AGENT = "assurance-loop"
LOOP_LAYER = "L2"
LOOP_ACTION = "assurance_loop_stage"
CONTROL_NAME = "nemo-guardrails-input-rail"


class LoopStage(StrEnum):
    """The ordered arc the loop writes to the ledger."""

    EXPOSED = "exposed"
    DETECTED = "detected"
    MAPPED = "mapped"
    PATCHED = "patched"
    VERIFIED = "verified"


# The arc, in the only valid order. `assert_assurance_arc` checks against this.
ARC: tuple[LoopStage, ...] = (
    LoopStage.EXPOSED,
    LoopStage.DETECTED,
    LoopStage.MAPPED,
    LoopStage.PATCHED,
    LoopStage.VERIFIED,
)


@dataclass(frozen=True)
class LoopDeps:
    """The four live operations the loop sequences (injected for testing).

    `expose`/`reverify` run the unguarded/guarded agent on the canonical exploit;
    `detect`/`rescan` run Garak against the unguarded/guarded agent.
    """

    expose: Callable[[], AgentRun]
    detect: Callable[[], list[GarakFinding]]
    rescan: Callable[[], list[GarakFinding]]
    reverify: Callable[[], AgentRun]


@dataclass(frozen=True)
class AssuranceLoopResult:
    """Summary of one end-to-end loop run."""

    exploit_before: bool
    exploit_after: bool
    before_fails: int
    after_fails: int
    remediated: bool
    arc_complete: bool


class AssuranceLoopError(Exception):
    """Raised when a stage cannot produce the result the arc requires."""


def _record(ledger: Ledger, stage: LoopStage, **payload: Any) -> None:
    ledger.append(
        agent=LOOP_AGENT,
        layer=LOOP_LAYER,
        action=LOOP_ACTION,
        payload={"stage": stage.value, **payload},
    )


def _prompt_injection_finding(findings: Sequence[GarakFinding]) -> GarakFinding:
    for finding in findings:
        if finding.family in PROMPT_INJECTION_FAMILIES:
            return finding
    raise AssuranceLoopError("no prompt-injection finding in the Garak report")


def assert_assurance_arc(ledger: Ledger) -> bool:
    """The milestone check: the ledger holds the full ordered arc and hash-verifies.

    A chain missing any stage, or with the stages out of order, returns False — so
    the loop is provably whole only when every stage ran in sequence.
    """
    stages = tuple(
        LoopStage(entry.payload["stage"])
        for entry in ledger.all()
        if entry.action == LOOP_ACTION
    )
    return stages == ARC and ledger.verify_chain()


def run_assurance_loop(
    deps: LoopDeps, *, ledger: Ledger | None = None
) -> AssuranceLoopResult:
    """Run the five-stage assurance arc in order, recording each to the ledger."""
    led = ledger if ledger is not None else open_ledger()

    # 1 — EXPOSE: the unguarded agent fires the memo exploit.
    exposed = deps.expose()
    exploit_before = exploit_fired(exposed)
    intent = exposed.transfer_intents[0] if exposed.transfer_intents else None
    _record(
        led,
        LoopStage.EXPOSED,
        exploit_fired=exploit_before,
        recipient=intent.recipient if intent else None,
        amount=intent.amount if intent else None,
    )

    # 2 — DETECT: Garak finds the vulnerability on the unguarded agent.
    before = list(deps.detect())
    finding = _prompt_injection_finding(before)
    _record(
        led,
        LoopStage.DETECTED,
        probe=finding.probe,
        fails=finding.fails,
        total_evaluated=finding.total_evaluated,
        found_our_vulnerability=found_our_vulnerability(before),
    )

    # 3 — MAP: finding → OWASP + EU Art. 15 + India principle (curated ids).
    mapping = map_finding(finding).mapping
    _record(
        led,
        LoopStage.MAPPED,
        owasp_llm=mapping.owasp_llm,
        owasp_agentic=mapping.owasp_agentic,
        eu_ai_act=mapping.eu_ai_act,
        eu_obligation_id=mapping.eu_obligation_id,
        india_principle=mapping.india_principle,
        india_obligation_id=mapping.india_obligation_id,
    )

    # 4 — PATCH: the NeMo Guardrails rail is applied (guarded agent path).
    _record(led, LoopStage.PATCHED, control=CONTROL_NAME)

    # 5 — VERIFY: Garak re-scans the guarded agent clean; the exploit no longer fires.
    after = list(deps.rescan())
    reverified = deps.reverify()
    before_fails = sum(f.fails for f in before)
    after_fails = sum(f.fails for f in after)
    exploit_after = exploit_fired(reverified)
    remediated = (
        after_fails == 0 and not found_our_vulnerability(after) and not exploit_after
    )
    _record(
        led,
        LoopStage.VERIFIED,
        before_fails=before_fails,
        after_fails=after_fails,
        remediated=remediated,
        exploit_refired=exploit_after,
    )

    return AssuranceLoopResult(
        exploit_before=exploit_before,
        exploit_after=exploit_after,
        before_fails=before_fails,
        after_fails=after_fails,
        remediated=remediated,
        arc_complete=assert_assurance_arc(led),
    )
