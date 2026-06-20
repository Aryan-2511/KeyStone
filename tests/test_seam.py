"""The L2↔L1 seam milestone (KS-0403) — the thesis-closing test.

Deterministic, fast — no LLM, no network. Proves the STRONG claim: ONE transaction
is simultaneously a financial crime (caught by the memo-blind FATF engine) AND an
AI-security vulnerability (its memo carries the canonical injection signature the
assurance loop flags). Bound on a shared TRANSACTION ID, against the SINGLE
canonical signature object (drift on either side fails the build).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from keystone.assurance import (
    CANONICAL_MEMO_EXPLOIT,
    MEMO_INJECTION_SIGNATURE,
    SeamProof,
    prove_seam,
    resolve_signature,
    seam_fraud_stream,
)
from keystone.assurance import seam as seam_module
from keystone.assurance.seam import SEAM_ACTION, SEAM_AGENT
from keystone.core.fatf import LEDGER_ACTION as FATF_ACTION
from keystone.core.fatf import Typology, detect
from keystone.core.ledger import Ledger

# --- THE STRONG ASSERTION: same transaction, both detections (milestone) -------


@pytest.mark.milestone
def test_one_transaction_is_both_financial_crime_and_ai_vulnerability() -> None:
    proof = prove_seam()
    assert isinstance(proof, SeamProof)

    # Layer 1 — the FATF engine flags THIS transaction as structuring (financial).
    assert proof.fatf_finding.typology is Typology.STRUCTURING
    assert proof.transaction_id in proof.fatf_finding.transaction_ids

    # Layer 2 — THAT SAME transaction carries the canonical injection signature,
    # and it is the SAME object the assurance loop tests for (identity, not a copy).
    assert proof.signature is MEMO_INJECTION_SIGNATURE

    # The binding is one transaction id, not a coincidence of two fixtures.
    stream, seam_id = seam_fraud_stream()
    assert proof.transaction_id == seam_id
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert resolve_signature(seam_txn.memo) is MEMO_INJECTION_SIGNATURE


# --- single source of truth (the memo IS the canonical payload) ---------------


def test_seam_memo_is_the_canonical_exploit_literal() -> None:
    stream, seam_id = seam_fraud_stream()
    seam_txn = next(t for t in stream if t.id == seam_id)
    assert seam_txn.memo == CANONICAL_MEMO_EXPLOIT.memo  # imported, not redefined
    assert CANONICAL_MEMO_EXPLOIT.signature is MEMO_INJECTION_SIGNATURE


def test_resolve_signature_is_the_canonical_object() -> None:
    assert resolve_signature(CANONICAL_MEMO_EXPLOIT.memo) is MEMO_INJECTION_SIGNATURE
    assert resolve_signature("Invoice #4471 for March hosting") is None


# --- memo-blindness re-proved on the seam fraud specifically ------------------


def test_fatf_catches_the_seam_regardless_of_memo() -> None:
    # The seam fraud is caught on FINANCIAL grounds — blanking the injection memo
    # does not change the FATF findings at all (AML detection is memo-blind).
    stream, seam_id = seam_fraud_stream()
    blanked = [
        t.model_copy(update={"memo": ""}) if t.id == seam_id else t for t in stream
    ]
    assert detect(stream) == detect(blanked)

    # The seam tx is still flagged as structuring with NO memo (financial grounds).
    structuring = [
        f
        for f in detect(blanked)
        if f.typology is Typology.STRUCTURING and seam_id in f.transaction_ids
    ]
    assert structuring


# --- ledger binding: one tx id, both findings ---------------------------------


def test_ledger_binds_one_tx_to_both_detections(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "seam.db")
    proof = prove_seam(ledger=ledger)
    entries = ledger.all()

    # Layer-1 finding implicating the seam transaction id.
    fatf_entries = [e for e in entries if e.action == FATF_ACTION]
    assert any(
        proof.transaction_id in e.payload["transaction_ids"] for e in fatf_entries
    )

    # The seam-binding entry: same tx id, carries the Layer-2 signature.
    binding = [e for e in entries if e.action == SEAM_ACTION]
    assert len(binding) == 1
    payload = binding[0].payload
    assert binding[0].agent == SEAM_AGENT
    assert payload["transaction_id"] == proof.transaction_id
    assert payload["vulnerability_signature"] == MEMO_INJECTION_SIGNATURE.name
    assert payload["fatf_typology"] == Typology.STRUCTURING.value
    assert payload["memo_is_canonical_exploit"] is True
    assert ledger.verify_chain() is True


# --- determinism + drift guards (the build fails if a side decouples) ---------


def test_seam_is_deterministic() -> None:
    assert prove_seam().transaction_id == prove_seam().transaction_id


def test_seam_fails_loud_if_memo_stops_resolving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Drift guard: if the seam memo ever stopped carrying the signature, the
    # milestone fails loudly instead of silently passing.
    monkeypatch.setattr(seam_module, "resolve_signature", lambda _memo: None)
    with pytest.raises(seam_module.SeamError, match="does not resolve"):
        prove_seam()
