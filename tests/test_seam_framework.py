"""The Seam Framework (M1-01) — the abstraction's own guarantees, proven by test.

These assert the PROPERTIES the framework promises across every registered pair, as
distinct from the per-pair seam tests (`test_seam.py`, which prove P1 itself still
binds through the framework — the faithfulness proof):

(i)   the uniform INDEPENDENCE property — the crime detector never receives the
      attack channel, for every registered pair;
(ii)  the build-failing DRIFT assertion fires when a CLEAN pair's two sides are
      forced to disagree (and the real pair still binds once restored);
(iii) a BOUNDARY pair is representable and its "no typology fires" assertion works.

Deterministic, fast — no LLM, no network.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from keystone.assurance import (
    CANONICAL_MEMO_EXPLOIT,
    MEMO_INJECTION_SIGNATURE,
    REGISTERED_PAIRS,
    AttackChannel,
    AttackSide,
    CrimeSide,
    FinancialProjection,
    SeamDriftError,
    SeamEvent,
    SeamPair,
    SeamResult,
    bind,
    financial_projection_for,
)
from keystone.assurance.seam import P1_PAIR
from keystone.core.fatf import Typology, detect

# --- (i) the uniform independence property, for EVERY registered pair ----------


@pytest.mark.parametrize("pair", REGISTERED_PAIRS, ids=lambda p: p.pair_id)
def test_detector_never_receives_the_attack_channel(pair: SeamPair) -> None:
    projection = financial_projection_for(pair)
    assert isinstance(projection, FinancialProjection)
    # The financial projection carries NO attack-bearing field: every memo is blank,
    # whatever channel this pair's attack rides.
    assert all(txn.memo == "" for txn in projection.transactions)


@pytest.mark.parametrize(
    "pair",
    [p for p in REGISTERED_PAIRS if p.result is not SeamResult.BOUNDARY],
    ids=lambda p: p.pair_id,
)
def test_projection_strips_real_attack_content(pair: SeamPair) -> None:
    # The strip removes REAL attack content, not a no-op: in the raw event the
    # operative transaction carries an attack the recognizer resolves; in the
    # projection that same transaction is attack-free (and no longer resolves).
    event = pair.plant()
    assert event.operative_tx_id is not None
    raw_operative = next(t for t in event.stream if t.id == event.operative_tx_id)
    assert pair.attack.recognize(raw_operative) is pair.attack.signature

    projection = financial_projection_for(pair)
    proj_operative = next(
        t for t in projection.transactions if t.id == event.operative_tx_id
    )
    assert pair.attack.recognize(proj_operative) is None


@pytest.mark.parametrize(
    "pair",
    [p for p in REGISTERED_PAIRS if p.result is SeamResult.CLEAN],
    ids=lambda p: p.pair_id,
)
def test_detection_is_channel_invariant(pair: SeamPair) -> None:
    # The crime side reaches the SAME verdict with the attack channel present or
    # stripped — proof it never relied on it. (It only ever sees the projection.)
    event = pair.plant()
    on_projection = pair.crime.detect(financial_projection_for(pair))
    on_raw_financials = detect(event.stream)
    assert on_projection == on_raw_financials


# --- P1 binds cleanly THROUGH the framework (the first-instance proof) ---------


def test_p1_binds_clean_through_the_framework() -> None:
    binding = bind(P1_PAIR)
    assert binding.result is SeamResult.CLEAN
    assert binding.transaction_id is not None
    assert binding.crime_finding is not None
    assert binding.crime_finding.typology is Typology.STRUCTURING
    assert binding.transaction_id in binding.crime_finding.transaction_ids
    # single source of truth: the SAME canonical object, by identity.
    assert binding.signature is MEMO_INJECTION_SIGNATURE


# --- (ii) the build-failing drift assertion catches a forced break -------------


def test_drift_fires_when_crime_side_stops_implicating() -> None:
    # Force the financial side to disagree: name an operative tx the detector never
    # flags. The binding must fail loudly rather than silently pass.
    event = P1_PAIR.plant()
    broken = replace(
        P1_PAIR,
        plant=lambda: SeamEvent(stream=event.stream, operative_tx_id="TXN-999999"),
    )
    with pytest.raises(SeamDriftError, match="did not implicate"):
        bind(broken)


def test_drift_fires_when_attack_side_stops_resolving() -> None:
    # Force the attack side to disagree: the recognizer no longer resolves to the
    # canonical signature.
    broken = replace(
        P1_PAIR,
        attack=replace(P1_PAIR.attack, recognize=lambda _txn: None),
    )
    with pytest.raises(SeamDriftError, match="does not resolve"):
        bind(broken)


def test_pair_still_binds_after_the_forced_break_is_restored() -> None:
    # The drift guard is the only thing that changed — the real pair binds again.
    binding = bind(P1_PAIR)
    assert binding.result is SeamResult.CLEAN
    assert binding.signature is MEMO_INJECTION_SIGNATURE


# --- (iii) a BOUNDARY pair is first-class; its negative IS the result ----------


def _boundary_stub_pair() -> SeamPair:
    """A trivial BOUNDARY stub: an exfil-style attack that moves no money.

    Stands in for P4 (M1-04) to prove the STRUCTURE — no real exfil engine built.
    No transaction → no typology can fire → the seam provably does not bind.
    """
    return SeamPair(
        pair_id="P-stub-boundary",
        title="stub exfil boundary",
        attack=AttackSide(
            owasp_id="LLM06",
            name="Sensitive Information Disclosure",
            channel=AttackChannel.EXFIL,
            signature=MEMO_INJECTION_SIGNATURE,
            recognize=lambda _txn: None,
        ),
        crime=CrimeSide(typology=None, detect=lambda proj: detect(proj.transactions)),
        result=SeamResult.BOUNDARY,
        plant=lambda: SeamEvent(stream=(), operative_tx_id=None),
    )


def test_boundary_pair_binds_as_a_proven_negative() -> None:
    binding = bind(_boundary_stub_pair())
    assert binding.result is SeamResult.BOUNDARY
    # The negative IS the result: nothing fired, nothing bound.
    assert binding.transaction_id is None
    assert binding.crime_finding is None
    assert binding.signature is None


def test_boundary_drift_fires_if_a_typology_unexpectedly_fires() -> None:
    # If a BOUNDARY pair ever started moving money (a typology fires), the boundary
    # no longer holds — the build must fail.
    drifted = replace(_boundary_stub_pair(), plant=P1_PAIR.plant)
    with pytest.raises(SeamDriftError, match="boundary no longer holds"):
        bind(drifted)


def test_canonical_exploit_text_absent_from_p1_projection() -> None:
    # Concrete independence check on the anchor: the literal canonical exploit is in
    # the raw event but nowhere in the projection the detector sees.
    event = P1_PAIR.plant()
    assert any(t.memo == CANONICAL_MEMO_EXPLOIT.memo for t in event.stream)
    projection = financial_projection_for(P1_PAIR)
    assert all(
        CANONICAL_MEMO_EXPLOIT.memo not in t.memo for t in projection.transactions
    )
