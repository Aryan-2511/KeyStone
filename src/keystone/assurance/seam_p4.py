"""P4 — sensitive information disclosure × (none) — THE CHARACTERIZED BOUNDARY.

The seam matrix's honest negative (Axis B; OWASP LLM06, the "Vault Whisper" exfil
class, cf. arXiv:2601.22569). P4 is a PROVEN NON-BINDING, not a binding:

    The seam covers attacks that manifest as FUND MOVEMENT; it does NOT cover attacks
    that manifest as DATA LOSS. P4 is exactly that boundary, stated precisely.

An exfiltration injection coerces the agent to LEAK another party's data; NO money
moves, so the event's financial footprint is empty and NO transaction-monitoring
typology can fire on it. The negative is PRINCIPLED, not incidental: it is a property
of the ATTACK (a data-disclosure outcome produces no transaction record — there is
nothing for any typology to act on), not a gap in our detector coverage. We do NOT
force a weak positive ("unusual access before a transfer") — the clean negative IS the
result (M1-00 §4).

P4 is a framework INSTANCE using the BOUNDARY result the framework already supports
(M1-01): `bind` asserts ZERO typologies fire on the financial projection and returns
an all-`None` `PairBinding`; if a typology ever DID fire (someone later makes exfil
move money), the boundary fails the build — drift-protected like the CLEAN pairs.

No new framework, no new typology, no forced binding. Lives on the edge
(`keystone.assurance`); the core never imports it (import-linter KEPT).
"""

from __future__ import annotations

from keystone.core.fatf import Finding, detect
from keystone.core.transactions import Transaction

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
    CANONICAL_EXFIL_MEMO,
    EXFIL_INJECTION_SIGNATURE,
    VulnerabilitySignature,
)


def resolve_exfil_signature(text: str) -> VulnerabilitySignature | None:
    """Resolve an attack payload to P4's exfiltration signature, or None.

    Reuses the SAME shared detector P1-P3 use (`is_data_field_injection`, the KS-0302
    guard) and maps a positive detection to P4's canonical signature
    (`EXFIL_INJECTION_SIGNATURE`). This is how we show the P4 attack is REAL and present
    on the attack side — even though it binds to NO financial typology. Composition only.
    """
    if is_data_field_injection(text):
        return EXFIL_INJECTION_SIGNATURE
    return None


def p4_exfil_event() -> SeamEvent:
    """The P4 event: a data-exfiltration attack that moves NO money.

    The financial stream is EMPTY — not because we withheld data, but because the
    attack's outcome is DATA DISCLOSURE: leaked data has no representation in a
    transaction stream, so the attack produces no transfer record. There is therefore
    no operative transaction to bind on (`operative_tx_id=None`), which is exactly what
    a BOUNDARY pair expresses. The full typology suite, run over this projection, fires
    nothing — by NATURE of the attack, not absence of a detector.
    """
    return SeamEvent(stream=(), operative_tx_id=None)


def _p4_recognize(txn: Transaction) -> VulnerabilitySignature | None:
    """P4's attack recognizer (for uniformity with the CLEAN pairs).

    Indirects through the module-level `resolve_exfil_signature` (looked up at call
    time). `bind`'s BOUNDARY path never calls this — the boundary is proven by the
    ABSENCE of any typology, not by an operative transaction — but it is present so P4
    has the same shape as P1-P3, and the tests exercise it to show the attack is real.
    """
    return resolve_exfil_signature(txn.memo)


def _p4_detect(projection: FinancialProjection) -> list[Finding]:
    """P4's crime detector: the FULL memo-blind FATF suite over the financial projection.

    The complete typology suite (structuring / rapid-movement / large-transfer) — NOT a
    P4-specific detector — so the zero-fire result is the real suite finding nothing to
    fire on, not a missing rule.
    """
    return detect(projection.transactions)


# P4 expressed as a framework pair — the matrix's BOUNDARY (a proven non-binding).
# crime.typology is None: bind() requires ZERO findings of ANY typology to fire.
P4_PAIR = SeamPair(
    pair_id="P4",
    title="Sensitive Information Disclosure × (none) — the boundary",
    attack=AttackSide(
        owasp_id="LLM06",
        name="Sensitive Information Disclosure",
        channel=AttackChannel.EXFIL,
        signature=EXFIL_INJECTION_SIGNATURE,
        recognize=_p4_recognize,
    ),
    crime=CrimeSide(typology=None, detect=_p4_detect),
    result=SeamResult.BOUNDARY,
    plant=p4_exfil_event,
)

# The one-sentence boundary statement (feeds the M1-06 paper write-up directly).
BOUNDARY_STATEMENT = (
    "The seam covers attacks that manifest as fund movement; it does not cover attacks "
    "that manifest as data loss. P4 (sensitive-information disclosure) is that boundary."
)

# Re-exported for the principled-negative test: the canonical exfil payload.
__all__ = [
    "BOUNDARY_STATEMENT",
    "CANONICAL_EXFIL_MEMO",
    "EXFIL_INJECTION_SIGNATURE",
    "P4_PAIR",
    "p4_exfil_event",
    "resolve_exfil_signature",
]
