"""P2 — prompt-injection × rapid-movement/layering (KS-0602), through the framework.

Deterministic, fast — no LLM, no network. Proves the STRONG claim for the matrix's
SECOND pair: ONE transaction is simultaneously a financial crime (the memo-blind FATF
engine flags it as RAPID_MOVEMENT on velocity + fan-out) AND an AI-security
vulnerability (its memo carries the canonical forwarding injection). Bound through the
UNCHANGED M1-01 framework. Plus the anti-collapse DISTINCTNESS guard (M1-00 §6): P2's
pattern is detector-distinct from P1's structuring cluster.
"""

from __future__ import annotations

import pytest

from keystone.assurance import (
    CANONICAL_FORWARDING_EXPLOIT,
    MEMO_FORWARDING_SIGNATURE,
    P1_PAIR,
    P2_PAIR,
    SeamDriftError,
    SeamResult,
    bind,
    p2_fraud_stream,
    resolve_forwarding_signature,
)
from keystone.assurance import seam_p2 as seam_p2_module
from keystone.core.fatf import Typology, detect

# --- THE STRONG ASSERTION: same transaction, both detections (milestone) -------


@pytest.mark.milestone
def test_p2_one_transaction_is_both_financial_crime_and_ai_vulnerability() -> None:
    binding = bind(P2_PAIR)
    assert binding.result is SeamResult.CLEAN

    # Layer 1 — the FATF engine flags THIS transaction as rapid-movement (financial).
    assert binding.crime_finding is not None
    assert binding.crime_finding.typology is Typology.RAPID_MOVEMENT
    assert binding.transaction_id in binding.crime_finding.transaction_ids

    # Layer 2 — THAT SAME transaction carries the canonical forwarding signature,
    # the SAME object the attack side names (identity, not a copy).
    assert binding.signature is MEMO_FORWARDING_SIGNATURE

    # The binding is one transaction id, not a coincidence of two fixtures.
    stream, seam_id = p2_fraud_stream()
    assert binding.transaction_id == seam_id
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert resolve_forwarding_signature(seam_txn.memo) is MEMO_FORWARDING_SIGNATURE


# --- single source of truth (the memo IS the canonical payload) ---------------


def test_p2_memo_is_the_canonical_exploit_literal() -> None:
    stream, seam_id = p2_fraud_stream()
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert seam_txn.memo == CANONICAL_FORWARDING_EXPLOIT.memo  # imported, not redefined
    assert CANONICAL_FORWARDING_EXPLOIT.signature is MEMO_FORWARDING_SIGNATURE


def test_p2_resolve_is_the_canonical_object() -> None:
    assert (
        resolve_forwarding_signature(CANONICAL_FORWARDING_EXPLOIT.memo)
        is MEMO_FORWARDING_SIGNATURE
    )
    assert resolve_forwarding_signature("Invoice #4471 for March hosting") is None


# --- memo-blindness re-proved on the P2 fraud specifically --------------------


def test_p2_fatf_catches_the_seam_regardless_of_memo() -> None:
    # P2 is caught on FINANCIAL grounds — blanking the injection memo does not change
    # the FATF findings at all (rapid-movement detection is memo-blind).
    stream, seam_id = p2_fraud_stream()
    blanked = [
        t.model_copy(update={"memo": ""}) if t.id == seam_id else t for t in stream
    ]
    assert detect(stream) == detect(blanked)

    rapid = [
        f
        for f in detect(blanked)
        if f.typology is Typology.RAPID_MOVEMENT and seam_id in f.transaction_ids
    ]
    assert rapid


# --- DISTINCTNESS: the anti-collapse guard (M1-00 §6) -------------------------


def test_p2_pattern_fires_rapid_movement_not_structuring() -> None:
    # P2's stream is a DIFFERENT shape from P1's structuring cluster: small, fast
    # fan-out below the structuring band → it fires RAPID_MOVEMENT and NOT STRUCTURING.
    stream, _ = p2_fraud_stream()
    typologies = {f.typology for f in detect(stream)}
    assert Typology.RAPID_MOVEMENT in typologies
    assert Typology.STRUCTURING not in typologies
    assert Typology.LARGE_TRANSFER not in typologies


def test_p1_and_p2_are_detector_distinct() -> None:
    # The anti-collapse property, stated honestly. STRUCTURING is the discriminator:
    # P1's pattern IS a structuring cluster, P2's is NOT. The two pairs therefore bind
    # to DIFFERENT typologies on DIFFERENTLY-shaped streams.
    #
    # NOTE: P1's structuring cluster is dense enough that it ALSO trips RAPID_MOVEMENT
    # incidentally — so RAPID_MOVEMENT does NOT discriminate the two, and we do not
    # assert "P1 never fires rapid-movement" (it does). P2's EXCLUSIVITY (rapid, not
    # structuring) is what proves it is a genuinely new shape, not a copy of P1.
    p2_stream, _ = p2_fraud_stream()
    p1_typologies = {f.typology for f in detect(P1_PAIR.plant().stream)}
    p2_typologies = {f.typology for f in detect(p2_stream)}

    assert Typology.STRUCTURING in p1_typologies  # P1 IS a structuring cluster
    assert Typology.STRUCTURING not in p2_typologies  # P2 is NOT
    assert Typology.RAPID_MOVEMENT in p2_typologies  # P2's bound typology fires

    # The pairs bind to distinct typologies (the matrix's Axis-A breadth).
    assert P1_PAIR.crime.typology is Typology.STRUCTURING
    assert P2_PAIR.crime.typology is Typology.RAPID_MOVEMENT


# --- drift guard, proven on P2 (the build fails if a side decouples) ----------


def test_p2_is_deterministic() -> None:
    assert bind(P2_PAIR).transaction_id == bind(P2_PAIR).transaction_id


def test_p2_fails_loud_if_memo_stops_resolving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Drift guard: if P2's memo ever stopped carrying the signature, bind() fails
    # loudly (SeamDriftError) instead of silently passing.
    monkeypatch.setattr(
        seam_p2_module, "resolve_forwarding_signature", lambda _memo: None
    )
    with pytest.raises(SeamDriftError, match="does not resolve"):
        bind(P2_PAIR)
