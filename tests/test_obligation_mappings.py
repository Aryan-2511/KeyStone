"""The rigorous obligation mappings (M2-02) — the convergence claim, populated.

Deterministic, fast — no LLM, no network. Asserts the contract a green gate CAN check
about the registered evidence set: every mapping clears the four-part bar (real cited
obligation + requirement grounded in the control text + a specific non-empty reason +
a DERIVED state), every obligation ref resolves to a REAL L3 obligation, the
cross-jurisdiction modality spread is present (hard law + advisory, real per-obligation),
and the DPDP boundary is a principled NOT_EVIDENCED (data-protection ↔ data-loss, not
fund movement). The rigor of each *reason* is reviewed by reading it (the PR report).
"""

from __future__ import annotations

from keystone.assurance import REFERENCED_ASSURANCE
from keystone.convergence import (
    REFERENCE_MAPPING,
    REGISTERED_MAPPINGS,
    EvidenceKind,
    EvidenceState,
    ObligationRef,
    derive_state,
)
from keystone.core.obligations import load_obligations

_REAL = {o.id: o for o in load_obligations()}


# --- every mapping clears the four-part bar against REAL L3 -------------------


def test_every_mapping_refs_a_real_l3_obligation() -> None:
    assert len(REGISTERED_MAPPINGS) >= 4
    for m in REGISTERED_MAPPINGS:
        # The obligation ref is a REAL, existing L3 obligation, built from_obligation
        # (subsumed, never invented or a parallel registry).
        assert m.obligation.id in _REAL, m.obligation.id
        assert m.obligation == ObligationRef.from_obligation(_REAL[m.obligation.id])
        # Requirement grounded in the real control text + its framework spine.
        assert m.requirement.strip()
        # A specific, non-generic reason (not a drawn line on a slide).
        assert len(m.reason.strip()) > 80


def test_reference_mapping_is_in_the_set_not_duplicated() -> None:
    art15 = [m for m in REGISTERED_MAPPINGS if m.obligation.id == "OBL-EUAI-015"]
    assert len(art15) == 1
    assert REFERENCE_MAPPING in REGISTERED_MAPPINGS


# --- the cross-jurisdiction modality spread (M2-00 §4) ------------------------


def test_set_spans_hard_law_and_advisory_real_modality() -> None:
    evidenced = [m for m in REGISTERED_MAPPINGS if m.evidences]
    hard = [m for m in evidenced if m.obligation.modality == "HARD_LAW"]
    advisory = [m for m in evidenced if m.obligation.modality == "SELF_CERTIFICATION"]
    # The SAME seam event evidenced against obligations of DIFFERENT enforcement weight.
    assert hard and advisory
    assert any(m.obligation.id == "OBL-EUAI-015" for m in hard)  # EU Art. 15, hard law
    assert any(m.obligation.id == "OBL-RBI-001" for m in advisory)  # RBI, advisory
    # The modality is the obligation's REAL per-obligation value, not country-inferred.
    for m in evidenced:
        assert (
            m.obligation.modality == _REAL[m.obligation.id].enforcement_modality.value
        )
    # Cross-jurisdiction: both EU and India are represented.
    assert {m.obligation.jurisdiction for m in REGISTERED_MAPPINGS} >= {"EU", "INDIA"}


def test_evidenced_mappings_surface_iso42001_and_nist() -> None:
    # The §4 ISO 42001 + NIST framings are evidenced via the control spine of real
    # obligations (ISO/NIST are the control library's frameworks, not L3 obligations).
    for m in REGISTERED_MAPPINGS:
        if m.evidences:
            assert "ISO_42001" in m.requirement
            assert "NIST_AI_RMF" in m.requirement


# --- satisfy/violate is DERIVED across the whole set -------------------------


def test_evidenced_mappings_derive_violate_then_satisfy() -> None:
    for m in REGISTERED_MAPPINGS:
        if m.evidences:
            assert m.before_after is not None
            # Built from the real before/after — can't drift.
            assert m.before_after.before_fails == REFERENCED_ASSURANCE.before_fails
            assert m.before_after.after_fails == REFERENCED_ASSURANCE.after_fails
            # The temporal transition: violated pre-patch, satisfied post-patch.
            assert m.transition == (EvidenceState.VIOLATE, EvidenceState.SATISFY)


def test_state_follows_the_numbers_for_every_evidenced_mapping() -> None:
    # The change-the-numbers property holds across the set (inherited from M2-01): a
    # still-failing post-patch flips the satisfied state to VIOLATE — derived, not a flag.
    for m in REGISTERED_MAPPINGS:
        if m.evidences:
            assert m.before_after is not None
            still_failing = m.before_after.model_copy(update={"after_fails": 4})
            assert (
                derive_state(
                    fails=still_failing.after_fails,
                    exploit_fired=still_failing.exploit_after,
                )
                is EvidenceState.VIOLATE
            )


# --- the DPDP boundary is a principled NOT_EVIDENCED (M2-00 §4) ---------------


def test_dpdp_boundary_is_a_principled_not_evidenced() -> None:
    boundary = [m for m in REGISTERED_MAPPINGS if not m.evidences]
    assert len(boundary) == 1
    b = boundary[0]
    assert b.kind is EvidenceKind.NOT_EVIDENCED
    assert b.obligation.id == "OBL-DPDPA-008"  # a real DPDP data-protection obligation
    # No satisfy/violate state at the boundary — the event simply isn't evidence.
    assert b.before_after is None
    assert b.pre_state is None and b.post_state is None
    # But the reason is mandatory and states a real scoping (as principled as P4):
    # data-protection ↔ data-loss, NOT fund movement.
    assert b.reason.strip()
    low = b.reason.lower()
    assert "personal data" in low
    assert "fund movement" in low or "fund-movement" in low
    assert "p4" in low or "data-loss" in low or "data loss" in low
