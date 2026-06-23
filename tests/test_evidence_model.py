"""The Evidence Model (M2-01) — a seam event AS audit evidence for an obligation.

Deterministic, fast — no LLM, no network. Proves the M2-00 invariants: the relationship
carries the four-part rigor as STRUCTURE (obligation + requirement + mandatory reason +
a DERIVED satisfy/violate state), it SUBSUMES the existing L3 obligation (not a parallel
registry), the satisfy/violate state is DERIVED from the before/after data (change the
numbers → it changes), the boundary ("not evidenced") is first-class, and the model names
itself honestly (evidence reasoning, not a legal verdict).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from keystone.assurance import REFERENCED_ASSURANCE
from keystone.convergence import (
    EVIDENCE_DISCLAIMER,
    REFERENCE_CONTROL_ID,
    REFERENCE_MAPPING,
    REFERENCE_OBLIGATION_ID,
    BeforeAfter,
    EvidenceKind,
    EvidenceRelationship,
    EvidenceState,
    ObligationRef,
    SeamEventRef,
    derive_state,
)
from keystone.core.obligations import load_obligations

# --- the reference mapping clears the §2 four-part bar -------------------------


def test_reference_mapping_has_all_four_parts() -> None:
    m = REFERENCE_MAPPING
    # 1 — a real, cited obligation with its enforcement modality.
    assert m.obligation.id == REFERENCE_OBLIGATION_ID
    assert m.obligation.modality == "HARD_LAW"
    assert m.obligation.jurisdiction == "EU"
    assert m.obligation.provision  # the citation provision (Art. 15)
    # 2 — what the obligation requires (grounded in the real control text).
    assert m.requirement.strip()
    assert REFERENCE_CONTROL_ID in (m.requirement) or "robust" in m.requirement.lower()
    # 3 — a specific, non-empty reason WHY the event is evidence.
    assert len(m.reason.strip()) > 40
    assert "memo-injection" in m.reason or "injection" in m.reason.lower()
    # 4 — a satisfy/violate state, derived (below).
    assert m.kind is EvidenceKind.EVIDENCED
    assert m.before_after is not None
    # The seam event is P1, referenced (not redefined).
    assert m.seam_event.pair_id == "P1"
    assert m.seam_event.owasp_id == "LLM01"


def test_reference_mapping_subsumes_the_existing_l3_obligation() -> None:
    # The obligation ref is built FROM the real L3 obligation — not a parallel registry.
    obligations = {o.id: o for o in load_obligations()}
    assert REFERENCE_OBLIGATION_ID in obligations  # it is a REAL, existing obligation
    real = obligations[REFERENCE_OBLIGATION_ID]
    assert REFERENCE_MAPPING.obligation == ObligationRef.from_obligation(real)
    # Modality is the obligation's real per-obligation value, not country-inferred.
    assert REFERENCE_MAPPING.obligation.modality == real.enforcement_modality.value


# --- satisfy/violate is DERIVED from the before/after, not asserted ------------


def test_state_is_derived_from_the_numbers_not_a_flag() -> None:
    # The pure derivation: an attack that still succeeds VIOLATES; detected+blocked SATISFIES.
    assert derive_state(fails=10, exploit_fired=True) is EvidenceState.VIOLATE
    assert derive_state(fails=0, exploit_fired=False) is EvidenceState.SATISFY
    assert derive_state(fails=1, exploit_fired=False) is EvidenceState.VIOLATE
    assert derive_state(fails=0, exploit_fired=True) is EvidenceState.VIOLATE


def test_changing_the_before_after_numbers_changes_the_state() -> None:
    # Prove the state is NOT a hardcoded flag: doctor the post-patch numbers so the patch
    # "failed", and the satisfied state flips to VIOLATE — derived, not asserted.
    m = REFERENCE_MAPPING
    assert m.pre_state is EvidenceState.VIOLATE
    assert m.post_state is EvidenceState.SATISFY
    assert m.before_after is not None  # EVIDENCED ⇒ data present

    still_failing = m.before_after.model_copy(update={"after_fails": 3})
    drifted = m.model_copy(update={"before_after": still_failing})
    assert drifted.post_state is EvidenceState.VIOLATE  # the state followed the numbers

    # And a world where the attack never succeeded pre-patch would not be a violation.
    clean_pre = m.before_after.model_copy(
        update={"before_fails": 0, "exploit_before": False}
    )
    assert clean_pre.pre_state is EvidenceState.SATISFY


def test_mapping_state_cannot_drift_from_the_real_assurance_data() -> None:
    # The before/after equals the canonical REFERENCED_ASSURANCE (built from it), so the
    # satisfy/violate transition can't drift from what the assurance loop produced.
    ba = REFERENCE_MAPPING.before_after
    assert ba is not None
    assert ba.before_fails == REFERENCED_ASSURANCE.before_fails == 10
    assert ba.after_fails == REFERENCED_ASSURANCE.after_fails == 0


def test_mapping_carries_both_states_and_the_transition() -> None:
    # The contribution: the SAME obligation, violated then satisfied, one seam event.
    m = REFERENCE_MAPPING
    assert m.transition == (EvidenceState.VIOLATE, EvidenceState.SATISFY)
    assert m.before_after is not None and m.before_after.is_remediation is True


# --- the reason is MANDATORY (the anti-checklist guard) ------------------------


def test_a_relationship_without_a_reason_is_inadmissible() -> None:
    base = REFERENCE_MAPPING
    # Constructing with an empty / whitespace-only reason fails at the type boundary.
    for blank in ("", "   "):
        with pytest.raises(ValidationError):
            EvidenceRelationship(
                obligation=base.obligation,
                requirement=base.requirement,
                reason=blank,
                seam_event=base.seam_event,
                kind=EvidenceKind.EVIDENCED,
                before_after=base.before_after,
            )


def test_an_empty_requirement_is_inadmissible() -> None:
    base = REFERENCE_MAPPING
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            obligation=base.obligation,
            requirement="",
            reason=base.reason,
            seam_event=base.seam_event,
            kind=EvidenceKind.EVIDENCED,
            before_after=base.before_after,
        )


def test_evidenced_relationship_must_carry_before_after_data() -> None:
    # The state is derived from data — an EVIDENCED relationship cannot exist without it.
    base = REFERENCE_MAPPING
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            obligation=base.obligation,
            requirement=base.requirement,
            reason=base.reason,
            seam_event=base.seam_event,
            kind=EvidenceKind.EVIDENCED,
            before_after=None,
        )


# --- the BOUNDARY ("not evidenced by this event") is first-class ---------------


def test_boundary_relationship_is_representable() -> None:
    # Stub the §4 boundary (DPDP data-protection ↔ a fund-movement event) to prove the
    # STRUCTURE — without building the real M2-02 mapping. The negative IS a result.
    dpdp = next(o for o in load_obligations() if o.id.startswith("OBL-DPDPA-"))
    boundary = EvidenceRelationship(
        obligation=ObligationRef.from_obligation(dpdp),
        requirement="Protection of personal data held/processed by the Data Fiduciary.",
        reason=(
            "A fund-movement seam event (P1 structuring) moves money but touches no "
            "personal data — only the P4 exfil / data-loss class would evidence a "
            "data-protection obligation. This event does not evidence it."
        ),
        seam_event=SeamEventRef(
            pair_id="P1",
            owasp_id="LLM01",
            attack="Prompt Injection",
            title="Prompt Injection × Structuring",
        ),
        kind=EvidenceKind.NOT_EVIDENCED,
    )
    assert boundary.evidences is False
    # No satisfy/violate state at the boundary — the event simply isn't evidence.
    assert boundary.pre_state is None
    assert boundary.post_state is None
    assert boundary.transition is None
    # But a reason is STILL mandatory — the boundary is reasoned, not blank.
    assert boundary.reason.strip()


def test_boundary_relationship_must_not_carry_state_data() -> None:
    dpdp = next(o for o in load_obligations() if o.id.startswith("OBL-DPDPA-"))
    with pytest.raises(ValidationError):
        EvidenceRelationship(
            obligation=ObligationRef.from_obligation(dpdp),
            requirement="Protection of personal data.",
            reason="A fund-movement event does not evidence a data-protection obligation.",
            seam_event=REFERENCE_MAPPING.seam_event,
            kind=EvidenceKind.NOT_EVIDENCED,
            before_after=BeforeAfter(
                prompt_cap=12,
                before_fails=10,
                after_fails=0,
                exploit_before=True,
                exploit_after=False,
            ),
        )


# --- the honest "not lawyers" framing is encoded ------------------------------


def test_model_names_itself_as_evidence_reasoning_not_a_verdict() -> None:
    assert "NOT a legal" in EVIDENCE_DISCLAIMER
    assert "evidence reasoning" in EVIDENCE_DISCLAIMER.lower()
