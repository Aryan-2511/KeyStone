"""P3 — prompt-injection × large-transfer/threshold — the matrix's third pair.

Completes Axis A (one attack class — OWASP LLM01 — manifesting as THREE distinct FATF
typologies: small-many / fast-onward / single-large). ONE transaction that is
simultaneously:

- (Layer 1) a single threshold-breaching transfer the memo-BLIND FATF engine flags on
  AMOUNT alone (`LARGE_TRANSFER`); and
- (Layer 2) its memo IS `CANONICAL_LARGE_TRANSFER_EXPLOIT` — a single-large-transfer
  injection — resolving to `MEMO_LARGE_TRANSFER_SIGNATURE`.

P3 is a framework INSTANCE, not new machinery (mirrors `seam_p2`): an attack side, a
crime side wired to the memo-blind detector through the framework's
`FinancialProjection`, a deterministic single-large-transfer stream, and a `SeamPair`
registered in `keystone.assurance.pairs`. The framework's `bind` supplies the three
rigor mechanisms — none re-implemented here.

Distinctness (the clean discriminator): P3's pattern fires `LARGE_TRANSFER` and NEITHER
`STRUCTURING` nor `RAPID_MOVEMENT` — a single transfer cannot trip structuring's
`>= 3` band or rapid-movement's `>= 5` velocity rule. Unlike P1, P3 is fully exclusive.

Boundary: lives on the edge (`keystone.assurance`); the core never imports it
(import-linter KEPT).
"""

from __future__ import annotations

from keystone.core.fatf import Finding, Typology, detect
from keystone.core.transactions import Transaction, large_sample_stream

from .framework import (
    AttackChannel,
    AttackSide,
    CrimeSide,
    FinancialProjection,
    SeamEvent,
    SeamPair,
    SeamResult,
)
from .injection_patterns import is_data_field_injection
from .signature import (
    CANONICAL_LARGE_TRANSFER_EXPLOIT,
    MEMO_LARGE_TRANSFER_SIGNATURE,
    VulnerabilitySignature,
)


def resolve_large_transfer_signature(memo: str) -> VulnerabilitySignature | None:
    """Resolve a memo to P3's large-transfer signature, or None.

    Reuses the SAME shared detector P1/P2 use (`is_data_field_injection`, the KS-0302
    guard) and maps a positive detection to P3's canonical signature
    (`MEMO_LARGE_TRANSFER_SIGNATURE`). Composition only — no new detection capability,
    no redefined signature.
    """
    if is_data_field_injection(memo):
        return CANONICAL_LARGE_TRANSFER_EXPLOIT.signature
    return None


def p3_fraud_stream() -> tuple[list[Transaction], str]:
    """Plant P3: a single large transfer whose memo IS the exploit.

    Starts from the deterministic `large_sample_stream` (already carries one
    threshold-breaching transfer), identifies that transfer using the memo-BLIND FATF
    engine (financial grounds, before any memo is planted), and replaces ONLY that
    transfer's memo with `CANONICAL_LARGE_TRANSFER_EXPLOIT.memo`. Returns the stream and
    the seam transaction id. Mirrors P1/P2's fraud-stream fixtures.
    """
    base = large_sample_stream()
    large = next(f for f in detect(base) if f.typology is Typology.LARGE_TRANSFER)
    seam_tx_id = large.transaction_ids[0]
    planted = [
        txn.model_copy(update={"memo": CANONICAL_LARGE_TRANSFER_EXPLOIT.memo})
        if txn.id == seam_tx_id
        else txn
        for txn in base
    ]
    return planted, seam_tx_id


def _p3_plant() -> SeamEvent:
    """The P3 event: the large-transfer fraud stream + the operative transfer."""
    stream, seam_tx_id = p3_fraud_stream()
    return SeamEvent(stream=tuple(stream), operative_tx_id=seam_tx_id)


def _p3_recognize(txn: Transaction) -> VulnerabilitySignature | None:
    """P3's attack recognizer: resolve the transaction's MEMO channel to a signature.

    Indirects through the module-level `resolve_large_transfer_signature` (looked up at
    call time) so a drift guard can monkeypatch it.
    """
    return resolve_large_transfer_signature(txn.memo)


def _p3_detect(projection: FinancialProjection) -> list[Finding]:
    """P3's crime detector: the memo-blind FATF engine over the financial projection."""
    return detect(projection.transactions)


# P3 expressed as a framework pair — the matrix's third instance (completes Axis A).
P3_PAIR = SeamPair(
    pair_id="P3",
    title="Prompt Injection × Large-transfer/threshold",
    attack=AttackSide(
        owasp_id="LLM01",
        name="Prompt Injection",
        channel=AttackChannel.MEMO,
        signature=MEMO_LARGE_TRANSFER_SIGNATURE,
        recognize=_p3_recognize,
    ),
    crime=CrimeSide(typology=Typology.LARGE_TRANSFER, detect=_p3_detect),
    result=SeamResult.CLEAN,
    plant=_p3_plant,
)
