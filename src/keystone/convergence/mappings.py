"""The rigorous obligation mappings (M2-02) — the convergence claim, populated.

The full `REGISTERED_MAPPINGS` set: the P1 memo-injection seam event AS audit evidence
for a narrow-and-deep set of named, real L3 obligations, each clearing the M2-00 §2
four-part bar with a defensible reason grounded in the obligation's actual control text,
and a satisfy/violate state DERIVED from the before/after assurance data:

- **EU AI Act Art. 15** (`OBL-EUAI-015`, HARD LAW) — robustness/cybersecurity
  (`CTL-ROBUST-01`; ISO 42001 Clause 8 + NIST MEASURE). The M2-01 reference mapping.
- **EU AI Act Art. 9** (`OBL-EUAI-009`, HARD LAW) — risk identification + treatment
  (`CTL-RISK-01`; ISO 42001 6.1/8.2 + NIST MAP/MANAGE). The ISO-input-manipulation +
  NIST-semantic-threat framings.
- **RBI FREE-AI Sutra 1** (`OBL-RBI-001`, ADVISORY) — trust as foundation
  (`CTL-GOV-01`; ISO 42001 Clause 5 + NIST GOVERN). The India advisory half.
- **DPDP s. 8** (`OBL-DPDPA-008`) — the BOUNDARY: a data-protection obligation
  NOT_EVIDENCED by fund-movement events (evidenced only by the P4 exfil/data-loss class).

The set spans EU hard law + India advisory — the SAME seam event evidenced against
obligations of DIFFERENT enforcement weight (M2-00 §4). ISO 42001 and NIST AI RMF are the
control library's *frameworks* (not L3 obligations), so they are evidenced VIA the control
spine of the real obligations — never invented as standalone obligations. Every
`ObligationRef` is built FROM a real `keystone.core.obligations` obligation (subsumed, not
parallel). Lives on the edge; the core never imports it (import-linter KEPT).
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


def _evidenced(
    obligation_id: str, control_id: str, reason: str
) -> EvidenceRelationship:
    """Build an EVIDENCED relationship from real L3 data + the before/after (DERIVED).

    The seam event (P1 memo-injection) is the audit evidence; the satisfy/violate state
    is derived from `REFERENCED_ASSURANCE`. The requirement is grounded in the REAL
    control text (incl. its ISO 42001 / NIST / FATF spine).
    """
    return EvidenceRelationship(
        obligation=ObligationRef.from_obligation(_obligation_by_id(obligation_id)),
        requirement=_requirement_text(_control_by_id(control_id)),
        reason=reason,
        seam_event=_seam_event_ref(),
        kind=EvidenceKind.EVIDENCED,
        before_after=_before_after(),
    )


def _boundary(obligation_id: str, control_id: str, reason: str) -> EvidenceRelationship:
    """Build a NOT_EVIDENCED (boundary) relationship — a principled, reasoned non-mapping.

    No before/after, no satisfy/violate state: the fund-movement event simply is not
    evidence for this obligation. The reason states the scoping (M2-00 §4 boundary).
    """
    return EvidenceRelationship(
        obligation=ObligationRef.from_obligation(_obligation_by_id(obligation_id)),
        requirement=_requirement_text(_control_by_id(control_id)),
        reason=reason,
        seam_event=_seam_event_ref(),
        kind=EvidenceKind.NOT_EVIDENCED,
    )


def build_reference_mapping() -> EvidenceRelationship:
    """P1 × EU AI Act Art. 15 (`OBL-EUAI-015`, HARD LAW) — the M2-01 reference mapping."""
    return _evidenced(
        REFERENCE_OBLIGATION_ID,
        REFERENCE_CONTROL_ID,
        "The P1 memo-injection (OWASP LLM01) successfully manipulated the payments "
        "agent into an unauthorized transfer — a direct failure of the accuracy, "
        "robustness and cybersecurity Art. 15 requires of a high-risk AI system. The "
        "assurance loop's detect-and-patch (Garak found the vector, the NeMo Guardrails "
        "rail blocked it) is exactly the resilience/operational testing the control "
        "(CTL-ROBUST-01; ISO 42001 Clause 8, NIST MEASURE) names; the before/after IS "
        "that evidence.",
    )


def build_risk_management_mapping() -> EvidenceRelationship:
    """P1 × EU AI Act Art. 9 (`OBL-EUAI-009`, HARD LAW) — risk identification + treatment.

    Anchors the §4 "ISO 42001 input-manipulation risk treatment" + "NIST semantic-threat
    modeling" framings (CTL-RISK-01 → ISO 42001 6.1 & 8.2; NIST MAP and MANAGE).
    """
    return _evidenced(
        "OBL-EUAI-009",
        "CTL-RISK-01",
        "Art. 9 requires a risk-management system that identifies and evaluates known "
        "and reasonably foreseeable risks and adopts treatment measures across the "
        "lifecycle. The P1 memo-injection IS such a reasonably-foreseeable semantic "
        "attack — untrusted memo text treated as instructions. The assurance loop is the "
        "risk process the article requires made concrete: Garak red-teaming IDENTIFIED "
        "the vector (ISO 42001 6.1/8.2 risk assessment; NIST MAP threat modeling) and the "
        "Guardrails rail TREATED it (NIST MANAGE) — violated while the risk was untreated, "
        "satisfied once the treatment was in place.",
    )


def build_rbi_trust_mapping() -> EvidenceRelationship:
    """P1 × RBI FREE-AI Sutra 1 'Trust is the Foundation' (`OBL-RBI-001`, ADVISORY).

    The India advisory half of the modality spread (self-certification, not binding).
    """
    return _evidenced(
        "OBL-RBI-001",
        "CTL-GOV-01",
        "RBI FREE-AI Sutra 1 anchors AI adoption in TRUST — financial-sector systems "
        "must be reliable and inspire public confidence (an advisory committee principle, "
        "not a binding direction). The P1 attack directly undermines that trust: the "
        "agent was manipulated into moving laundered money. The assurance loop restores "
        "reliability (the vector detected and patched, 10/12 → 0/12) — the sutra "
        "evidenced as a governance control state (CTL-GOV-01; ISO 42001 Clause 5 "
        "leadership, NIST GOVERN). Advisory weight: self-certification, not fineable.",
    )


def build_dpdp_boundary() -> EvidenceRelationship:
    """The §4 BOUNDARY — DPDP s. 8 (`OBL-DPDPA-008`) NOT_EVIDENCED by fund-movement.

    As principled as the P4 matrix boundary: data-protection obligations are evidenced by
    DATA-LOSS events, not fund movement. The relationship is specific, not universal.
    """
    return _boundary(
        "OBL-DPDPA-008",
        "CTL-SEC-01",
        "DPDP s. 8 obliges the Data Fiduciary to protect PERSONAL DATA — its accuracy "
        "and completeness, reasonable security safeguards, and breach reporting. The P1 "
        "structuring event (and the other fund-movement events P2/P3/P5) move money but "
        "process or expose NO personal data, so they do not evidence a data-protection "
        "obligation. Only the P4 exfil / data-loss class — which leaks another party's "
        "data — would evidence it. The evidence relationship is specific: data-protection "
        "obligations are evidenced by data-loss events, not by fund movement.",
    )


#: The reference mapping — the evidence model's first instance (M2-01). Part of the
#: registered set below; kept as a named symbol for the M2-01 tests/UI.
REFERENCE_MAPPING: EvidenceRelationship = build_reference_mapping()

#: The full registered set of evidence relationships (M2-02) — the single source the
#: convergence result/UI (M2-0n) and the paper figure derive from. Spans EU hard law
#: (Art. 15, Art. 9) + India advisory (RBI Sutra 1), surfaces ISO 42001 + NIST via the
#: control spine, and includes the DPDP data-protection BOUNDARY (NOT_EVIDENCED).
REGISTERED_MAPPINGS: tuple[EvidenceRelationship, ...] = (
    REFERENCE_MAPPING,
    build_risk_management_mapping(),
    build_rbi_trust_mapping(),
    build_dpdp_boundary(),
)
