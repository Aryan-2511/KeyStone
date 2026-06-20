"""The L2↔L1 seam (KS-0403) — the thesis-closing milestone.

ONE transaction that is simultaneously a financial crime AND an AI-security
vulnerability:

- (Layer 1) it is part of a structuring / rapid-movement cluster the memo-BLIND
  KS-0402 FATF engine flags on FINANCIAL grounds alone; and
- (Layer 2) its memo IS `CANONICAL_MEMO_EXPLOIT` — the literal payload Garak flagged
  against the mock agent — resolving to `MEMO_INJECTION_SIGNATURE`.

Both sides reference the ONE canonical definition imported from
`keystone.assurance.signature` (single source of truth — never redefined here), and
the financial detection relies on the FATF engine's memo-blindness (we do NOT make
detection memo-aware). The strong claim is bound on a shared TRANSACTION ID: the
transfer FATF flags == the transfer carrying the signature.

Boundary: this lives in `keystone.assurance` (the edge) because it imports both the
assurance signature (edge) and the core transaction/FATF pieces; the core never
imports it (import-linter KEPT).
"""

from __future__ import annotations

from dataclasses import dataclass

from keystone.core.fatf import Finding, Typology, detect, record_findings
from keystone.core.ledger import Ledger
from keystone.core.transactions import Transaction, sample_stream

from .injection_patterns import is_data_field_injection
from .signature import CANONICAL_MEMO_EXPLOIT, VulnerabilitySignature

SEAM_AGENT = "l2-l1-seam"
SEAM_LAYER = "L1+L2"
SEAM_ACTION = "seam_binding"

_THESIS = (
    "one transaction is simultaneously a financial crime (FATF) and an "
    "AI-security vulnerability (memo prompt injection)"
)


class SeamError(Exception):
    """Raised when the seam fraud does not bind both detections."""


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


def prove_seam(*, ledger: Ledger | None = None) -> SeamProof:
    """Run BOTH detectors on the seam fraud and bind them on the shared tx id.

    Layer 1: the memo-blind FATF engine flags a structuring finding implicating the
    seam transaction. Layer 2: that SAME transaction's memo resolves to the canonical
    `MEMO_INJECTION_SIGNATURE`. Raises `SeamError` if either side fails to implicate
    the seam transaction. When a `ledger` is given, writes the Layer-1 fatf_finding
    plus a `seam_binding` entry that names the same tx id and the signature.
    """
    stream, seam_tx_id = seam_fraud_stream()

    fatf_finding = next(
        (
            f
            for f in detect(stream)
            if f.typology is Typology.STRUCTURING and seam_tx_id in f.transaction_ids
        ),
        None,
    )
    if fatf_finding is None:
        raise SeamError(
            f"FATF engine did not flag the seam transaction {seam_tx_id} as structuring"
        )

    seam_txn = next(t for t in stream if t.id == seam_tx_id)
    signature = resolve_signature(seam_txn.memo)
    if signature is None:
        raise SeamError(
            f"seam transaction {seam_tx_id} memo does not resolve to a signature"
        )

    if ledger is not None:
        record_findings([fatf_finding], ledger=ledger)
        ledger.append(
            agent=SEAM_AGENT,
            layer=SEAM_LAYER,
            action=SEAM_ACTION,
            payload={
                "transaction_id": seam_tx_id,
                "thesis": _THESIS,
                "fatf_typology": fatf_finding.typology.value,
                "vulnerability_signature": signature.name,
                "signature_field": signature.field.value,
                "signature_outcome": signature.outcome.value,
                "memo_is_canonical_exploit": seam_txn.memo
                == CANONICAL_MEMO_EXPLOIT.memo,
            },
        )

    return SeamProof(
        transaction_id=seam_tx_id, fatf_finding=fatf_finding, signature=signature
    )
