"""P3 — prompt-injection × large-transfer/threshold (KS-0603), through the framework.

Deterministic, fast — no LLM, no network. Proves the STRONG claim for the matrix's
THIRD pair (completing Axis A): ONE transaction is simultaneously a financial crime
(the memo-blind FATF engine flags it as LARGE_TRANSFER on amount alone) AND an
AI-security vulnerability (its memo carries the canonical single-large-transfer
injection). Bound through the UNCHANGED M1-01 framework. P3 is the cleanly-exclusive
pair: a single large transfer fires LARGE_TRANSFER and NEITHER other typology.
"""

from __future__ import annotations

import pytest

from keystone.assurance import (
    CANONICAL_LARGE_TRANSFER_EXPLOIT,
    MEMO_LARGE_TRANSFER_SIGNATURE,
    P3_PAIR,
    SeamDriftError,
    SeamResult,
    bind,
    p3_fraud_stream,
    resolve_large_transfer_signature,
)
from keystone.assurance import seam_p3 as seam_p3_module
from keystone.core.fatf import Typology, detect

# --- THE STRONG ASSERTION: same transaction, both detections (milestone) -------


@pytest.mark.milestone
def test_p3_one_transaction_is_both_financial_crime_and_ai_vulnerability() -> None:
    binding = bind(P3_PAIR)
    assert binding.result is SeamResult.CLEAN

    # Layer 1 — the FATF engine flags THIS transaction as a large transfer (financial).
    assert binding.crime_finding is not None
    assert binding.crime_finding.typology is Typology.LARGE_TRANSFER
    assert binding.transaction_id in binding.crime_finding.transaction_ids

    # Layer 2 — THAT SAME transaction carries the canonical large-transfer signature,
    # the SAME object the attack side names (identity, not a copy).
    assert binding.signature is MEMO_LARGE_TRANSFER_SIGNATURE

    # The binding is one transaction id, not a coincidence of two fixtures.
    stream, seam_id = p3_fraud_stream()
    assert binding.transaction_id == seam_id
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert (
        resolve_large_transfer_signature(seam_txn.memo) is MEMO_LARGE_TRANSFER_SIGNATURE
    )


# --- single source of truth (the memo IS the canonical payload) ---------------


def test_p3_memo_is_the_canonical_exploit_literal() -> None:
    stream, seam_id = p3_fraud_stream()
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert (
        seam_txn.memo == CANONICAL_LARGE_TRANSFER_EXPLOIT.memo
    )  # imported, not redefined
    assert CANONICAL_LARGE_TRANSFER_EXPLOIT.signature is MEMO_LARGE_TRANSFER_SIGNATURE


def test_p3_resolve_is_the_canonical_object() -> None:
    assert (
        resolve_large_transfer_signature(CANONICAL_LARGE_TRANSFER_EXPLOIT.memo)
        is MEMO_LARGE_TRANSFER_SIGNATURE
    )
    assert resolve_large_transfer_signature("Invoice #4471 for March hosting") is None


# --- memo-blindness re-proved on the P3 fraud specifically --------------------


def test_p3_fatf_catches_the_seam_regardless_of_memo() -> None:
    # P3 is caught on FINANCIAL grounds — blanking the injection memo does not change
    # the FATF findings at all (large-transfer detection is memo-blind, on amount).
    stream, seam_id = p3_fraud_stream()
    blanked = [
        t.model_copy(update={"memo": ""}) if t.id == seam_id else t for t in stream
    ]
    assert detect(stream) == detect(blanked)

    large = [
        f
        for f in detect(blanked)
        if f.typology is Typology.LARGE_TRANSFER and seam_id in f.transaction_ids
    ]
    assert large


# --- DISTINCTNESS: P3 is the cleanly-EXCLUSIVE pair --------------------------


def test_p3_pattern_fires_large_transfer_only() -> None:
    # A single threshold-breaching transfer fires LARGE_TRANSFER and NEITHER other
    # typology — it cannot trip structuring's >=3 band or rapid-movement's >=5 velocity
    # rule. Unlike P1 (whose dense cluster also trips rapid-movement), P3 is fully
    # exclusive — no overlap caveat needed.
    stream, _ = p3_fraud_stream()
    typologies = {f.typology for f in detect(stream)}
    assert Typology.LARGE_TRANSFER in typologies
    assert Typology.STRUCTURING not in typologies
    assert Typology.RAPID_MOVEMENT not in typologies


# --- drift guard, proven on P3 (the build fails if a side decouples) ----------


def test_p3_is_deterministic() -> None:
    assert bind(P3_PAIR).transaction_id == bind(P3_PAIR).transaction_id


def test_p3_fails_loud_if_memo_stops_resolving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Drift guard: if P3's memo ever stopped carrying the signature, bind() fails loudly
    # (SeamDriftError) instead of silently passing.
    monkeypatch.setattr(
        seam_p3_module, "resolve_large_transfer_signature", lambda _memo: None
    )
    with pytest.raises(SeamDriftError, match="does not resolve"):
        bind(P3_PAIR)
