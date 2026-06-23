"""P4 — sensitive information disclosure × (none) — THE CHARACTERIZED BOUNDARY.

Deterministic, fast — no LLM, no network. P4 is the matrix's PROVEN NEGATIVE (the
paper's credibility anchor): an OWASP LLM06 exfiltration attack that moves NO money, so
NO transaction-monitoring typology fires and the seam provably does NOT bind. These
tests prove the negative is PRINCIPLED (a property of the attack — data loss is not a
fund movement) and not incidental (not a missing detector), and that the boundary is
build-protected against an accidental future binding.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from keystone.assurance import (
    BOUNDARY_STATEMENT,
    CANONICAL_EXFIL_MEMO,
    EXFIL_INJECTION_SIGNATURE,
    P1_PAIR,
    P2_PAIR,
    P3_PAIR,
    P4_PAIR,
    ExploitOutcome,
    SeamDriftError,
    SeamResult,
    bind,
    financial_projection_for,
    p2_fraud_stream,
    p3_fraud_stream,
    p4_exfil_event,
    resolve_exfil_signature,
    seam_fraud_stream,
)
from keystone.core.fatf import detect

# --- P4 registers as a PROVEN BOUNDARY (the negative IS the result) -----------


@pytest.mark.milestone
def test_p4_binds_as_a_proven_boundary() -> None:
    binding = bind(P4_PAIR)
    assert binding.result is SeamResult.BOUNDARY
    # The proven non-binding: nothing fired, nothing bound.
    assert binding.transaction_id is None
    assert binding.crime_finding is None
    assert binding.signature is None
    assert P4_PAIR.crime.typology is None  # no typology to bind — by design


# --- the attack is REAL and present on the attack side ------------------------


def test_p4_exfil_attack_is_real_but_moves_no_money() -> None:
    # The attack is genuinely present: the exfil payload resolves to the canonical
    # signature (it IS a real injection, caught by the shared KS-0302 detector)...
    assert resolve_exfil_signature(CANONICAL_EXFIL_MEMO) is EXFIL_INJECTION_SIGNATURE
    # ...but its OUTCOME is DATA DISCLOSURE — not any fund-movement outcome. That is the
    # structural reason no typology can fire: the attack's product is leaked data.
    assert EXFIL_INJECTION_SIGNATURE.outcome is ExploitOutcome.DATA_DISCLOSURE
    assert EXFIL_INJECTION_SIGNATURE.outcome not in {
        ExploitOutcome.UNAUTHORIZED_INITIATE_TRANSFER,
        ExploitOutcome.UNAUTHORIZED_ONWARD_TRANSFER,
        ExploitOutcome.UNAUTHORIZED_LARGE_TRANSFER,
    }


# --- THE PRINCIPLED NEGATIVE: zero fires BY NATURE of the attack --------------


def test_p4_negative_is_principled_not_incidental() -> None:
    # (1) The exfil attack produces NO fund movement: its financial footprint is empty,
    # because a data-disclosure outcome has no representation in a transaction stream.
    event = p4_exfil_event()
    assert event.stream == ()
    assert event.operative_tx_id is None

    # (2) The FULL typology suite (structuring / rapid-movement / large-transfer), run
    # over P4's financial projection, fires NOTHING — there is nothing to fire on.
    projection = financial_projection_for(P4_PAIR)
    assert detect(projection.transactions) == []

    # (3) NOT incidental: the SAME `detect` suite DOES fire on fund-movement attacks
    # (P1/P2/P3). The detector is fully capable — the zero on P4 is a property of the
    # ATTACK (data loss is not a fund movement), not a missing rule.
    assert detect(seam_fraud_stream()[0]) != []
    assert detect(p2_fraud_stream()[0]) != []
    assert detect(p3_fraud_stream()[0]) != []


# --- the boundary is BUILD-PROTECTED against accidental binding ----------------


def test_p4_boundary_fails_loud_if_a_typology_ever_fires() -> None:
    # If a future change ever made the exfil attack move money (a typology fires on its
    # projection), the boundary no longer holds — bind() must fail the build, exactly as
    # it drift-protects the CLEAN pairs. Force it by swapping in a fund-movement stream.
    drifted = replace(P4_PAIR, plant=P1_PAIR.plant)
    with pytest.raises(SeamDriftError, match="boundary no longer holds"):
        bind(drifted)


def test_p4_boundary_holds_after_the_forced_break_is_restored() -> None:
    # The real pair still binds as the proven negative — only the forced plant changed.
    assert bind(P4_PAIR).result is SeamResult.BOUNDARY


# --- independence is still coherent for P4 ------------------------------------


def test_p4_detector_still_only_sees_the_financial_projection() -> None:
    # The crime detector receives the FinancialProjection (empty here) — never the attack
    # channel. The independence property holds trivially but coherently for the boundary.
    projection = financial_projection_for(P4_PAIR)
    assert all(txn.memo == "" for txn in projection.transactions)


# --- the one-sentence boundary statement (for the M1-06 paper write-up) -------


def test_p4_boundary_statement_is_the_characterization() -> None:
    assert "fund movement" in BOUNDARY_STATEMENT
    assert "data loss" in BOUNDARY_STATEMENT
    assert P1_PAIR.result is SeamResult.CLEAN
    assert P2_PAIR.result is SeamResult.CLEAN
    assert P3_PAIR.result is SeamResult.CLEAN
    assert P4_PAIR.result is SeamResult.BOUNDARY
