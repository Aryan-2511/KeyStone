"""P2 — prompt-injection × rapid-movement/layering — the matrix's second pair.

Movement 1's first test that the M1-01 framework *generalises* (Axis A: same attack
class as P1 — OWASP LLM01 prompt injection — a NEW typology). ONE transaction that is
simultaneously:

- (Layer 1) part of a rapid-movement / layering cluster the memo-BLIND FATF engine
  flags on velocity + fan-out alone (`RAPID_MOVEMENT`); and
- (Layer 2) its memo IS `CANONICAL_FORWARDING_EXPLOIT` — a forwarding/layering
  injection — resolving to `MEMO_FORWARDING_SIGNATURE`.

P2 is a framework INSTANCE, not new machinery: it provides an attack side, a crime
side wired to the memo-blind detector through the framework's `FinancialProjection`,
a deterministic rapid-movement stream (distinct from P1's structuring cluster), and a
`SeamPair` registered in `keystone.assurance.pairs`. The framework's `bind` supplies
the three rigor mechanisms (single source of truth, demonstration-not-coincidence,
build-failing drift) — none are re-implemented here.

Distinctness (M1-00 §6, the anti-collapse requirement): P2's pattern fires
`RAPID_MOVEMENT` and NOT `STRUCTURING` (its amounts sit below the structuring band) —
a visibly different shape (fast small fan-out, not a sub-threshold band). See
`tests/test_seam_p2.py`.

Boundary: lives on the edge (`keystone.assurance`); the core never imports it
(import-linter KEPT).
"""

from __future__ import annotations

from keystone.core.fatf import Finding, Typology, detect
from keystone.core.transactions import Transaction, rapid_sample_stream

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
    CANONICAL_FORWARDING_EXPLOIT,
    MEMO_FORWARDING_SIGNATURE,
    VulnerabilitySignature,
)


def resolve_forwarding_signature(memo: str) -> VulnerabilitySignature | None:
    """Resolve a memo to P2's forwarding signature, or None.

    Reuses the SAME shared detector P1 uses (`is_data_field_injection`, the KS-0302
    guard) and maps a positive detection to P2's canonical signature
    (`MEMO_FORWARDING_SIGNATURE`). Composition only — no new detection capability, no
    redefined signature.
    """
    if is_data_field_injection(memo):
        return CANONICAL_FORWARDING_EXPLOIT.signature
    return None


def p2_fraud_stream() -> tuple[list[Transaction], str]:
    """Plant P2: a rapid-movement cluster where one transfer's memo IS the exploit.

    Starts from the deterministic `rapid_sample_stream` (already carries a FATF
    rapid-movement cluster), identifies the cluster's operative transfer using the
    memo-BLIND FATF engine (financial grounds, before any memo is planted), and
    replaces ONLY that transfer's memo with `CANONICAL_FORWARDING_EXPLOIT.memo`.
    Returns the stream and the seam transaction id. Mirrors P1's `seam_fraud_stream`.
    """
    base = rapid_sample_stream()
    rapid = next(f for f in detect(base) if f.typology is Typology.RAPID_MOVEMENT)
    seam_tx_id = rapid.transaction_ids[0]
    planted = [
        txn.model_copy(update={"memo": CANONICAL_FORWARDING_EXPLOIT.memo})
        if txn.id == seam_tx_id
        else txn
        for txn in base
    ]
    return planted, seam_tx_id


def _p2_plant() -> SeamEvent:
    """The P2 event: the rapid-movement fraud stream + the operative transfer."""
    stream, seam_tx_id = p2_fraud_stream()
    return SeamEvent(stream=tuple(stream), operative_tx_id=seam_tx_id)


def _p2_recognize(txn: Transaction) -> VulnerabilitySignature | None:
    """P2's attack recognizer: resolve the transaction's MEMO channel to a signature.

    Indirects through the module-level `resolve_forwarding_signature` (looked up at
    call time) so a drift guard can monkeypatch it.
    """
    return resolve_forwarding_signature(txn.memo)


def _p2_detect(projection: FinancialProjection) -> list[Finding]:
    """P2's crime detector: the memo-blind FATF engine over the financial projection."""
    return detect(projection.transactions)


# P2 expressed as a framework pair — the matrix's second instance (Axis A).
P2_PAIR = SeamPair(
    pair_id="P2",
    title="Prompt Injection × Rapid-movement/layering",
    attack=AttackSide(
        owasp_id="LLM01",
        name="Prompt Injection",
        channel=AttackChannel.MEMO,
        signature=MEMO_FORWARDING_SIGNATURE,
        recognize=_p2_recognize,
    ),
    crime=CrimeSide(typology=Typology.RAPID_MOVEMENT, detect=_p2_detect),
    result=SeamResult.CLEAN,
    plant=_p2_plant,
)
