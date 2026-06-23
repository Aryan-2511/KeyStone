"""P5 — excessive agency / tool-misuse × unauthorized-recipient (KS-0605), Axis B.

Deterministic, fast — no LLM, no network. The matrix's OPEN pair, built via PATH A: a
NEW, minimal, INDEPENDENT recipient-screening typology (UNAUTHORIZED_RECIPIENT) catches
a tool-misuse payment (OWASP LLM08 — a DIFFERENT attack class than P1-P4's injection) to
a STANDING flagged destination. These tests prove P5 binds CLEAN as-found, that the
screen is genuinely independent of the attack (it fires on the standing list even with
NO attack present), and that the new typology is distinct from the three fund-movement
ones.
"""

from __future__ import annotations

import datetime

import pytest

from keystone.assurance import (
    CANONICAL_TOOL_MISUSE_MEMO,
    P5_PAIR,
    TOOL_MISUSE_SIGNATURE,
    InjectionField,
    InjectionMechanism,
    SeamDriftError,
    SeamResult,
    bind,
    p5_tool_misuse_stream,
    resolve_tool_misuse_signature,
)
from keystone.assurance import seam_p5 as seam_p5_module
from keystone.core.fatf import FLAGGED_DESTINATIONS, Typology, detect
from keystone.core.transactions import Currency, Transaction, TransactionType

# --- THE STRONG ASSERTION: same payment, both detections (milestone) -----------


@pytest.mark.milestone
def test_p5_one_payment_is_both_financial_crime_and_ai_vulnerability() -> None:
    binding = bind(P5_PAIR)
    assert binding.result is SeamResult.CLEAN

    # Layer 1 — the FATF engine flags THIS payment as an unauthorized recipient
    # (financial: the destination is on the standing screening list).
    assert binding.crime_finding is not None
    assert binding.crime_finding.typology is Typology.UNAUTHORIZED_RECIPIENT
    assert binding.transaction_id in binding.crime_finding.transaction_ids

    # Layer 2 — THAT SAME payment carries the canonical tool-misuse trace, the SAME
    # object the attack side names (identity, not a copy).
    assert binding.signature is TOOL_MISUSE_SIGNATURE

    stream, seam_id = p5_tool_misuse_stream()
    assert binding.transaction_id == seam_id
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert resolve_tool_misuse_signature(seam_txn.memo) is TOOL_MISUSE_SIGNATURE


# --- single source of truth (the memo IS the canonical tool-call trace) --------


def test_p5_memo_is_the_canonical_tool_call_trace() -> None:
    stream, seam_id = p5_tool_misuse_stream()
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert seam_txn.memo == CANONICAL_TOOL_MISUSE_MEMO  # imported, not redefined
    # the canonical trace is the single source of truth — it resolves to P5's signature.
    assert (
        resolve_tool_misuse_signature(CANONICAL_TOOL_MISUSE_MEMO)
        is TOOL_MISUSE_SIGNATURE
    )


def test_p5_resolve_is_the_canonical_object() -> None:
    assert (
        resolve_tool_misuse_signature(CANONICAL_TOOL_MISUSE_MEMO)
        is TOOL_MISUSE_SIGNATURE
    )
    # NOT an injection detector — a plain payment memo does not resolve.
    assert resolve_tool_misuse_signature("Invoice #4471 for March hosting") is None


# --- P5 is Axis B: a DIFFERENT attack class than the injection pairs -----------


def test_p5_attack_is_excessive_agency_not_injection() -> None:
    assert P5_PAIR.attack.owasp_id == "LLM08"
    assert TOOL_MISUSE_SIGNATURE.field is InjectionField.TOOL_CALL
    assert TOOL_MISUSE_SIGNATURE.mechanism is InjectionMechanism.EXCESSIVE_AGENCY


# --- memo-blindness re-proved on the P5 fraud specifically --------------------


def test_p5_screen_catches_the_seam_regardless_of_memo() -> None:
    # The recipient screen fires on the DESTINATION — blanking the tool-call trace does
    # not change the FATF findings at all (the screen is memo-blind).
    stream, seam_id = p5_tool_misuse_stream()
    blanked = [
        t.model_copy(update={"memo": ""}) if t.id == seam_id else t for t in stream
    ]
    assert detect(stream) == detect(blanked)

    flagged = [
        f
        for f in detect(blanked)
        if f.typology is Typology.UNAUTHORIZED_RECIPIENT
        and seam_id in f.transaction_ids
    ]
    assert flagged


# --- INDEPENDENCE: the standing list exists independently of the attack --------


def test_p5_flagged_list_is_a_standing_attack_independent_screen() -> None:
    # The list is STANDING core data: a non-trivial fixed set of flagged ids, defined
    # with NO reference to P5's attack (it is just account ids — a sanctions-style list).
    assert len(FLAGGED_DESTINATIONS) >= 3
    assert seam_p5_module._P5_FLAGGED_DESTINATION in FLAGGED_DESTINATIONS


def test_p5_screen_fires_on_the_destination_even_with_no_attack_present() -> None:
    # The strongest independence proof: a payment to a flagged destination with a BENIGN
    # memo (NO tool-call trace, NO attack at all) STILL fires UNAUTHORIZED_RECIPIENT.
    # The screen flags the destination on its own standing terms — it does NOT fire
    # because the attack named the recipient.
    benign_flagged = Transaction(
        id="TXN-000500",
        timestamp=datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC),
        sender_account="ACC-0007",
        recipient_account=sorted(FLAGGED_DESTINATIONS)[0],
        amount=2500.0,
        currency=Currency.USD,
        tx_type=TransactionType.TRANSFER,
        memo="Invoice payment",
    )
    findings = detect([benign_flagged])
    assert any(f.typology is Typology.UNAUTHORIZED_RECIPIENT for f in findings)
    # And resolving the attack on that benign payment yields nothing — no attack present.
    assert resolve_tool_misuse_signature(benign_flagged.memo) is None


# --- DISTINCTNESS: UNAUTHORIZED_RECIPIENT is distinct from the three ----------


def test_p5_pattern_fires_unauthorized_recipient_only() -> None:
    # A single moderate payment to a flagged destination fires UNAUTHORIZED_RECIPIENT and
    # NEITHER structuring (needs >=3 in-band) nor rapid-movement (needs >=5) nor
    # large-transfer (needs >=CTR) — a new signal type (list membership), distinct from
    # the three intrinsic-pattern typologies.
    stream, _ = p5_tool_misuse_stream()
    typologies = {f.typology for f in detect(stream)}
    assert Typology.UNAUTHORIZED_RECIPIENT in typologies
    assert Typology.STRUCTURING not in typologies
    assert Typology.RAPID_MOVEMENT not in typologies
    assert Typology.LARGE_TRANSFER not in typologies


# --- drift guard, proven on P5 ------------------------------------------------


def test_p5_is_deterministic() -> None:
    assert bind(P5_PAIR).transaction_id == bind(P5_PAIR).transaction_id


def test_p5_fails_loud_if_tool_trace_stops_resolving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Drift guard: if P5's tool-call trace ever stopped resolving, bind() fails loudly
    # (SeamDriftError) instead of silently passing.
    monkeypatch.setattr(
        seam_p5_module, "resolve_tool_misuse_signature", lambda _memo: None
    )
    with pytest.raises(SeamDriftError, match="does not resolve"):
        bind(P5_PAIR)
