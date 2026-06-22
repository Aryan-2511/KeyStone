"""P1 — prompt-injection × structuring — the Seam Framework's FIRST instance.

The thesis-closing milestone (KS-0403), now expressed THROUGH the Seam Framework
(`keystone.assurance.framework`, M1-01). ONE transaction that is simultaneously a
financial crime AND an AI-security vulnerability:

- (Layer 1) it is part of a structuring cluster the memo-BLIND KS-0402 FATF engine
  flags on FINANCIAL grounds alone; and
- (Layer 2) its memo IS `CANONICAL_MEMO_EXPLOIT` — the literal payload Garak flagged
  against the mock agent — resolving to `MEMO_INJECTION_SIGNATURE`.

P1 is no longer special-cased: it is a `SeamPair` (`P1_PAIR`) bound by the
framework's `bind`, which inherits the three rigor mechanisms (single source of
truth, demonstration-not-coincidence, build-failing drift) and the uniform
independence guarantee (the detector only ever sees the financial projection, never
the memo). P1 still passing through the framework is the proof the abstraction is
faithful. `prove_seam` / `seam_fraud_stream` / `resolve_signature` keep their
signatures so existing callers (the Layer-1 milestone, the demo) are unchanged.

Boundary: this lives in `keystone.assurance` (the edge); the core never imports it
(import-linter KEPT).
"""

from __future__ import annotations

from dataclasses import dataclass

from keystone.core.fatf import Finding, Typology, detect, record_findings
from keystone.core.ledger import Ledger
from keystone.core.transactions import Transaction, sample_stream

from .framework import (
    AttackChannel,
    AttackSide,
    CrimeSide,
    FinancialProjection,
    SeamDriftError,
    SeamEvent,
    SeamPair,
    SeamResult,
    bind,
)
from .injection_patterns import is_data_field_injection
from .signature import (
    CANONICAL_MEMO_EXPLOIT,
    MEMO_INJECTION_SIGNATURE,
    VulnerabilitySignature,
)

SEAM_AGENT = "l2-l1-seam"
SEAM_LAYER = "L1+L2"
SEAM_ACTION = "seam_binding"

_THESIS = (
    "one transaction is simultaneously a financial crime (FATF) and an "
    "AI-security vulnerability (memo prompt injection)"
)


class SeamError(Exception):
    """Raised when the P1 seam fraud does not bind both detections."""


@dataclass(frozen=True)
class SeamProof:
    """The bound proof: ONE transaction id, both detections, the canonical signature."""

    transaction_id: str
    fatf_finding: Finding
    signature: VulnerabilitySignature


def resolve_signature(memo: str) -> VulnerabilitySignature | None:
    """Resolve a memo to the vulnerability signature it carries, or None.

    Reuses the SAME detector the KS-0302 guard uses (`is_data_field_injection`) and
    maps a positive detection to the canonical signature (`CANONICAL_MEMO_EXPLOIT`'s
    signature, which IS `MEMO_INJECTION_SIGNATURE`). Composition only — no new
    detection capability, no redefined signature.
    """
    if is_data_field_injection(memo):
        return CANONICAL_MEMO_EXPLOIT.signature
    return None


def seam_fraud_stream() -> tuple[list[Transaction], str]:
    """Plant the seam: a structuring cluster where one transfer's memo IS the exploit.

    Starts from the KS-0401 `sample_stream` (already carries a FATF structuring
    cluster), identifies the cluster's operative transfer using the memo-BLIND FATF
    engine (financial grounds, before any memo is planted), and replaces ONLY that
    transfer's memo with `CANONICAL_MEMO_EXPLOIT.memo`. Returns the stream and the
    seam transaction id. No new transaction capability — generator + imported constant.
    """
    base = sample_stream()
    structuring = next(f for f in detect(base) if f.typology is Typology.STRUCTURING)
    seam_tx_id = structuring.transaction_ids[0]
    planted = [
        txn.model_copy(update={"memo": CANONICAL_MEMO_EXPLOIT.memo})
        if txn.id == seam_tx_id
        else txn
        for txn in base
    ]
    return planted, seam_tx_id


def _p1_plant() -> SeamEvent:
    """The P1 event: the seam fraud stream + the operative (memo-bearing) transfer."""
    stream, seam_tx_id = seam_fraud_stream()
    return SeamEvent(stream=tuple(stream), operative_tx_id=seam_tx_id)


def _p1_recognize(txn: Transaction) -> VulnerabilitySignature | None:
    """P1's attack recognizer: resolve the transaction's MEMO channel to a signature.

    Indirects through the module-level `resolve_signature` (looked up at call time)
    so the drift guard can monkeypatch it.
    """
    return resolve_signature(txn.memo)


def _p1_detect(projection: FinancialProjection) -> list[Finding]:
    """P1's crime detector: the memo-blind FATF engine over the financial projection."""
    return detect(projection.transactions)


# P1 expressed as a framework pair — the FIRST instance of the seam matrix.
P1_PAIR = SeamPair(
    pair_id="P1",
    title="Prompt Injection × Structuring",
    attack=AttackSide(
        owasp_id="LLM01",
        name="Prompt Injection",
        channel=AttackChannel.MEMO,
        signature=MEMO_INJECTION_SIGNATURE,
        recognize=_p1_recognize,
    ),
    crime=CrimeSide(typology=Typology.STRUCTURING, detect=_p1_detect),
    result=SeamResult.CLEAN,
    plant=_p1_plant,
)


def prove_seam(*, ledger: Ledger | None = None) -> SeamProof:
    """Bind P1 through the framework and (optionally) record it to the ledger.

    Delegates the detection + binding rigor to the framework's `bind` (Layer 1 = the
    memo-blind FATF engine on the financial projection; Layer 2 = the operative tx
    memo resolving to the canonical `MEMO_INJECTION_SIGNATURE`; bound on the shared
    tx id). Raises `SeamError` if either side fails to implicate the seam transaction.
    When a `ledger` is given, writes the Layer-1 fatf_finding plus a `seam_binding`
    entry that names the same tx id and the signature.
    """
    try:
        binding = bind(P1_PAIR)
    except SeamDriftError as exc:
        raise SeamError(str(exc)) from exc

    if (
        binding.transaction_id is None
        or binding.crime_finding is None
        or binding.signature is None
    ):
        raise SeamError("P1 seam did not bind both detections")

    proof = SeamProof(
        transaction_id=binding.transaction_id,
        fatf_finding=binding.crime_finding,
        signature=binding.signature,
    )

    if ledger is not None:
        stream, seam_tx_id = seam_fraud_stream()
        seam_txn = next(t for t in stream if t.id == seam_tx_id)
        record_findings([proof.fatf_finding], ledger=ledger)
        ledger.append(
            agent=SEAM_AGENT,
            layer=SEAM_LAYER,
            action=SEAM_ACTION,
            payload={
                "transaction_id": proof.transaction_id,
                "thesis": _THESIS,
                "fatf_typology": proof.fatf_finding.typology.value,
                "vulnerability_signature": proof.signature.name,
                "signature_field": proof.signature.field.value,
                "signature_outcome": proof.signature.outcome.value,
                "memo_is_canonical_exploit": seam_txn.memo
                == CANONICAL_MEMO_EXPLOIT.memo,
            },
        )

    return proof
