"""The Layer-1 milestone (KS-0405) — compose the existing pieces, NAT-orchestrated.

Builds NO new capability: it sequences the KS-0401 stream + KS-0402 memo-blind FATF
engine + KS-0403 seam binding + KS-0404 report/sign-off into one end-to-end arc and
records it to the evidence ledger:

    INGESTED → DETECTED → SEAM_BOUND → REPORTED → SIGNED

The SEAM_BOUND stage proves the fraud L1 caught carries the EXACT
`MEMO_INJECTION_SIGNATURE` that Layer 2 already found and patched (KS-0304) — by
signature identity (the single canonical object) plus a ledger cross-reference. It
REFERENCES the proven L2 finding; it does NOT re-run the assurance loop / Garak /
Guardrails.

`run_layer1_milestone` is the deterministic spine: it runs the stages in order,
each writing one `layer1_milestone_stage` ledger entry, with the LLM narrative
INJECTED (`narrate`) so the fast gate exercises the exact sequencing over a canned
narrative — no Ollama, no network. `assert_layer1_arc` is the milestone check.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from keystone.core.fatf import Typology, detect
from keystone.core.ledger import Ledger, open_ledger
from keystone.core.reporting import (
    Report,
    ReportFacts,
    ReportFormat,
    assemble_facts,
    sign_off,
    to_finnet,
)
from keystone.llm.report_narrative import GuardedNarrative

from .seam import resolve_signature, seam_fraud_stream
from .signature import MEMO_INJECTION_SIGNATURE

MILESTONE_AGENT = "layer1-milestone"
MILESTONE_LAYER = "L1"
MILESTONE_ACTION = "layer1_milestone_stage"
DEFAULT_SIGNER = "compliance.officer@keystone"

# How the SEAM stage cites the already-proven Layer-2 finding (reference, not re-run).
_L2_REFERENCE = (
    "Same canonical MEMO_INJECTION_SIGNATURE the Layer-2 assurance loop (KS-0304) "
    "found (Garak) and patched (NeMo Guardrails) — referenced, not re-run."
)

# A narrative generator: facts -> guarded narrative (injected; live = the LLM edge).
Narrator = Callable[[ReportFacts], GuardedNarrative]


class Layer1Stage(StrEnum):
    """The ordered Layer-1 arc written to the ledger."""

    INGESTED = "ingested"
    DETECTED = "detected"
    SEAM_BOUND = "seam_bound"
    REPORTED = "reported"
    SIGNED = "signed"


ARC: tuple[Layer1Stage, ...] = (
    Layer1Stage.INGESTED,
    Layer1Stage.DETECTED,
    Layer1Stage.SEAM_BOUND,
    Layer1Stage.REPORTED,
    Layer1Stage.SIGNED,
)


class Layer1MilestoneError(Exception):
    """Raised when a stage cannot produce the result the arc requires."""


@dataclass(frozen=True)
class Layer1Result:
    """Summary of one end-to-end Layer-1 arc run."""

    seam_transaction_id: str
    fatf_typology: str
    l2_signature: str
    narrative_fell_back: bool
    signed_by: str
    arc_complete: bool


def _record(ledger: Ledger, stage: Layer1Stage, **payload: Any) -> None:
    ledger.append(
        agent=MILESTONE_AGENT,
        layer=MILESTONE_LAYER,
        action=MILESTONE_ACTION,
        payload={"stage": stage.value, **payload},
    )


def assert_layer1_arc(ledger: Ledger) -> bool:
    """The milestone check: the ledger holds the full ordered arc and hash-verifies.

    A chain missing any stage, or with the stages out of order, returns False.
    """
    stages = tuple(
        Layer1Stage(entry.payload["stage"])
        for entry in ledger.all()
        if entry.action == MILESTONE_ACTION
    )
    return stages == ARC and ledger.verify_chain()


def run_layer1_milestone(
    *,
    narrate: Narrator,
    signer: str = DEFAULT_SIGNER,
    ledger: Ledger | None = None,
) -> Layer1Result:
    """Run the five-stage Layer-1 arc in order, recording each to the ledger."""
    led = ledger if ledger is not None else open_ledger()

    # 1 — INGEST: the stream incl. the structuring cluster whose operative tx carries
    # CANONICAL_MEMO_EXPLOIT (KS-0401 + KS-0403 fixture).
    stream, seam_tx_id = seam_fraud_stream()
    _record(
        led,
        Layer1Stage.INGESTED,
        transaction_count=len(stream),
        seam_transaction_id=seam_tx_id,
    )

    # 2 — DETECT: the memo-blind FATF engine flags the structuring fraud (KS-0402).
    finding = next(
        (
            f
            for f in detect(stream)
            if f.typology is Typology.STRUCTURING and seam_tx_id in f.transaction_ids
        ),
        None,
    )
    if finding is None:
        raise Layer1MilestoneError(
            f"FATF engine did not flag the seam transaction {seam_tx_id}"
        )
    _record(
        led,
        Layer1Stage.DETECTED,
        typology=finding.typology.value,
        account=finding.account,
        transaction_ids=list(finding.transaction_ids),
        implicates_seam_tx=seam_tx_id in finding.transaction_ids,
    )

    # 3 — SEAM: the flagged tx carries the SAME signature L2 found & patched (KS-0403
    # binding). Reference the L2 finding by signature identity; do NOT re-run L2.
    seam_txn = next(t for t in stream if t.id == seam_tx_id)
    signature = resolve_signature(seam_txn.memo)
    if signature is not MEMO_INJECTION_SIGNATURE:
        raise Layer1MilestoneError(
            f"seam transaction {seam_tx_id} memo did not resolve to the L2 signature"
        )
    _record(
        led,
        Layer1Stage.SEAM_BOUND,
        transaction_id=seam_tx_id,
        l2_signature=signature.name,
        l2_reference=_L2_REFERENCE,
        thesis="the fraud L1 caught carries the exact vulnerability L2 found and patched",
    )

    # 4 — REPORT: facts → FINnet report → guarded narrative (KS-0404).
    facts = assemble_facts(finding, stream)
    narrative = narrate(facts)
    report = Report(
        facts=facts,
        narrative=narrative.text,
        narrative_fell_back=narrative.fell_back,
    )
    _record(
        led,
        Layer1Stage.REPORTED,
        report_format=ReportFormat.FINNET.value,
        narrative=report.narrative,
        narrative_fell_back=report.narrative_fell_back,
        total_amount=facts.total_amount,
        transaction_count=facts.transaction_count,
        finnet_report=to_finnet(report),
    )

    # 5 — SIGN: human checkpoint, draft → signed (KS-0404).
    signed = sign_off(report, signer)
    _record(
        led,
        Layer1Stage.SIGNED,
        status=signed.status.value,
        signed_by=signer,
    )

    return Layer1Result(
        seam_transaction_id=seam_tx_id,
        fatf_typology=finding.typology.value,
        l2_signature=signature.name,
        narrative_fell_back=report.narrative_fell_back,
        signed_by=signer,
        arc_complete=assert_layer1_arc(led),
    )
