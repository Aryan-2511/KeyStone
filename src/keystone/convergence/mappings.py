"""The reference evidence mapping (M2-01) — P1 × EU AI Act Art. 15, the first instance.

ONE rigorous evidence relationship, built end-to-end from the REAL system data, to prove
the evidence model works (the analog of M1-01's "P1 is the framework's first instance").
The other obligations' mappings (ISO 42001, NIST AI RMF, RBI, the DPDP boundary) are
M2-02+ — NOT built here.

The reference mapping: the **P1 memo-injection seam event** is the audit evidence for
**EU AI Act Art. 15** (`OBL-EUAI-015`, hard law) — the obligation's robustness/
cybersecurity control (`CTL-ROBUST-01`; ISO 42001 Clause 8 + NIST AI RMF MEASURE). It
clears the M2-00 §2 four-part bar:

1. obligation — `OBL-EUAI-015`, built FROM the existing L3 graph (not a parallel one).
2. requirement — the real `CTL-ROBUST-01` control text the obligation crosswalks onto.
3. reason — the memo-injection IS the accuracy/robustness/cybersecurity failure Art. 15
   names; the assurance loop's detect-and-patch is the resilience testing it requires.
4. state — DERIVED from `REFERENCED_ASSURANCE` (10/12 → 0/12): VIOLATE pre-patch,
   SATISFY post-patch — the same obligation, both states, one seam event.

Boundary: lives on the edge; the core never imports it (import-linter KEPT).
"""

from __future__ import annotations

from keystone.assurance import P1_PAIR, REFERENCED_ASSURANCE
from keystone.core.controls import Control, load_controls
from keystone.core.obligations import Obligation, load_obligations

from .evidence import (
    BeforeAfter,
    EvidenceKind,
    EvidenceRelationship,
    ObligationRef,
    SeamEventRef,
)

# The reference mapping's anchors (real ids in the L3 graph + the matrix).
REFERENCE_OBLIGATION_ID = "OBL-EUAI-015"
REFERENCE_CONTROL_ID = "CTL-ROBUST-01"


def _obligation_by_id(obligation_id: str) -> Obligation:
    """Load one obligation from the EXISTING L3 graph (the source of truth)."""
    for obligation in load_obligations():
        if obligation.id == obligation_id:
            return obligation
    raise KeyError(f"obligation {obligation_id!r} not found in the L3 graph")


def _control_by_id(control_id: str) -> Control:
    """Load one control from the EXISTING shared control library."""
    for control in load_controls():
        if control.id == control_id:
            return control
    raise KeyError(f"control {control_id!r} not found in the control library")


def _requirement_text(control: Control) -> str:
    """What the obligation requires, grounded in the REAL control text + its spine."""
    spine = "; ".join(f"{m.framework.value} {m.reference}" for m in control.spine)
    return f"{control.title}: {control.description} (crosswalk: {spine})"


def _seam_event_ref() -> SeamEventRef:
    """The P1 seam event, referenced from the matrix (M1 is NOT modified)."""
    return SeamEventRef(
        pair_id=P1_PAIR.pair_id,
        owasp_id=P1_PAIR.attack.owasp_id,
        attack=P1_PAIR.attack.name,
        title=P1_PAIR.title,
    )


def _before_after() -> BeforeAfter:
    """The before/after the state derives from — built FROM REFERENCED_ASSURANCE."""
    ra = REFERENCED_ASSURANCE
    return BeforeAfter(
        prompt_cap=ra.prompt_cap,
        before_fails=ra.before_fails,
        after_fails=ra.after_fails,
        exploit_before=ra.exploit_before,
        exploit_after=ra.exploit_after,
    )


def build_reference_mapping() -> EvidenceRelationship:
    """Assemble the P1 × Art. 15 evidence relationship from the real system data."""
    obligation = _obligation_by_id(REFERENCE_OBLIGATION_ID)
    control = _control_by_id(REFERENCE_CONTROL_ID)
    return EvidenceRelationship(
        obligation=ObligationRef.from_obligation(obligation),
        requirement=_requirement_text(control),
        reason=(
            "The P1 memo-injection (OWASP LLM01) successfully manipulated the payments "
            "agent into an unauthorized transfer — a direct failure of the accuracy, "
            "robustness and cybersecurity Art. 15 requires of a high-risk AI system. The "
            "assurance loop's detect-and-patch (Garak found the vector, the NeMo "
            "Guardrails rail blocked it) is exactly the resilience/operational testing "
            "the control (CTL-ROBUST-01) names; the before/after IS that evidence."
        ),
        seam_event=_seam_event_ref(),
        kind=EvidenceKind.EVIDENCED,
        before_after=_before_after(),
    )


#: The reference mapping — the evidence model's first instance (M2-01). M2-02+ grows this
#: into the full set of rigorous obligation mappings.
REFERENCE_MAPPING: EvidenceRelationship = build_reference_mapping()
