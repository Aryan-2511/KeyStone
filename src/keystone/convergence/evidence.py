"""The Evidence Model (M2-01) — a seam event AS audit evidence for an obligation.

Movement 2's architectural core. It turns "an AI-security finding is *analogous* to a
compliance failure" into "a seam event *is* the audit evidence that satisfies-or-violates
a named, real regulatory obligation" (M2-00 §1). A typed `EvidenceRelationship` binds a
seam event to an EXISTING Layer-3 obligation and carries the M2-00 §2 four-part rigor AS
STRUCTURE, so an inadmissible mapping literally cannot be constructed:

1. `obligation` — a real, cited obligation (built FROM the existing `keystone.core`
   obligation graph, never a parallel registry).
2. `requirement` — what the obligation actually requires (the specific control text).
3. `reason` — WHY this seam event is evidence for/against it. MANDATORY and non-empty
   (the anti-"checklist RegTech" guard, M2-00 §2): no relationship without a reason.
4. state — SATISFY / VIOLATE, DERIVED from the before/after assurance data (M2-00 §3),
   never passed as a static flag. The relationship carries BOTH states + the temporal
   transition (violated pre-patch → satisfied post-patch) and the numbers behind it.

A `NOT_EVIDENCED` relationship (the boundary, M2-00 §4) is first-class — "this event does
NOT evidence this obligation" with a stated reason — mirroring how M1-01 made the seam
BOUNDARY a first-class result.

> **Not a legal determination.** This model represents *defensible technical-compliance
> evidence reasoning* — "this event is an instance of the risk this control names" — NOT
> legal advice or a certified compliance opinion (M2-00 §6). The satisfy/violate model is
> a defensible *simplification* of compliance, grounded in real before/after data; real
> audits weigh more factors. Named honestly so the UI never mistakes it for automated
> compliance judgment.

Boundary: lives in `keystone.convergence` (governance/edge logic over L3 + seam events);
the deterministic core stays unaware of it (import-linter KEPT).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from keystone.core.obligations import Obligation

#: The honest framing the UI must surface — this is evidence reasoning, not a verdict.
EVIDENCE_DISCLAIMER = (
    "Defensible technical-compliance evidence reasoning — that this event is an instance "
    "of the risk a control names — NOT a legal opinion or a certified compliance "
    "determination. The satisfy/violate model is a before/after simplification."
)


class EvidenceState(StrEnum):
    """The compliance state a seam event evidences AT A MOMENT (M2-00 §3).

    Not a static property of the obligation — the SAME obligation is VIOLATED pre-patch
    (the attack succeeded) and SATISFIED post-patch (detected + blocked). Derived from
    the assurance data; never asserted.
    """

    VIOLATE = "VIOLATE"
    SATISFY = "SATISFY"


class EvidenceKind(StrEnum):
    """Whether a seam event evidences an obligation at all (M2-00 §4).

    EVIDENCED — the event is audit evidence for the obligation (carries satisfy/violate).
    NOT_EVIDENCED — the boundary: this event does NOT evidence this obligation, with a
    stated reason (e.g. a data-protection obligation is evidenced by data-loss, not
    fund-movement, events). The negative is a first-class outcome, not an error.
    """

    EVIDENCED = "EVIDENCED"
    NOT_EVIDENCED = "NOT_EVIDENCED"


def derive_state(*, fails: int, exploit_fired: bool) -> EvidenceState:
    """Derive the compliance state from assurance signals — the core of M2-00 §3.

    The obligation is VIOLATED while the attack succeeds (any probe still fails, or the
    exploit still fires); it is SATISFIED only once the vulnerability is detected AND
    blocked (no failing probes, no exploit). A pure function of the numbers, so the state
    can never drift from the real before/after data.
    """
    if fails > 0 or exploit_fired:
        return EvidenceState.VIOLATE
    return EvidenceState.SATISFY


class BeforeAfter(BaseModel):
    """The before/after assurance data the satisfy/violate state DERIVES from (M2-00 §3).

    Mirrors the canonical `keystone.assurance.REFERENCED_ASSURANCE` (~10/12 → 0/12): the
    pre-patch state derives from `before_fails`/`exploit_before`, the post-patch state
    from `after_fails`/`exploit_after`. Built FROM the referenced result, so the
    transition can't drift from what the assurance loop actually produced.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    prompt_cap: int
    before_fails: int
    after_fails: int
    exploit_before: bool
    exploit_after: bool

    @property
    def pre_state(self) -> EvidenceState:
        """The VIOLATE state — the attack succeeded before the patch."""
        return derive_state(fails=self.before_fails, exploit_fired=self.exploit_before)

    @property
    def post_state(self) -> EvidenceState:
        """The SATISFY state — detected + blocked after the patch."""
        return derive_state(fails=self.after_fails, exploit_fired=self.exploit_after)

    @property
    def is_remediation(self) -> bool:
        """True iff the transition is VIOLATE → SATISFY (the controlled state)."""
        return (
            self.pre_state is EvidenceState.VIOLATE
            and self.post_state is EvidenceState.SATISFY
        )


class ObligationRef(BaseModel):
    """A reference to an EXISTING Layer-3 obligation — never a parallel registry.

    Built from a `keystone.core.obligations.Obligation` (the source of truth) so the
    evidence model SUBSUMES L3 rather than duplicating it. Carries the cited identity +
    the real per-obligation enforcement modality (read, never country-inferred).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    instrument: str
    jurisdiction: str
    modality: str
    provision: str
    title: str

    @classmethod
    def from_obligation(cls, obligation: Obligation) -> Self:
        """Build the reference from a real L3 obligation (subsume, don't redefine)."""
        return cls(
            id=obligation.id,
            instrument=obligation.instrument.value,
            jurisdiction=obligation.jurisdiction.value,
            modality=obligation.enforcement_modality.value,
            provision=obligation.citation.provision,
            title=obligation.citation.title,
        )


class SeamEventRef(BaseModel):
    """A lightweight reference to the seam event being used as evidence.

    References the matrix's events by identity (the M1 framework is NOT modified). For
    the reference mapping this is P1 (memo-injection × structuring).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    pair_id: str
    owasp_id: str
    attack: str
    title: str


class EvidenceRelationship(BaseModel):
    """A seam event AS audit evidence for one obligation — the four-part rigor as STRUCTURE.

    EVIDENCED relationships carry the satisfy/violate states DERIVED from `before_after`;
    NOT_EVIDENCED (boundary) relationships carry no state, only the reason it does not
    evidence the obligation. A `reason` is mandatory in BOTH cases — the rigor bar.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    obligation: ObligationRef
    requirement: str
    reason: str
    seam_event: SeamEventRef
    kind: EvidenceKind = EvidenceKind.EVIDENCED
    # The before/after data EVIDENCED relationships derive their state from. Required iff
    # EVIDENCED; absent for a boundary (which has no satisfy/violate state).
    before_after: BeforeAfter | None = None

    @field_validator("requirement", "reason")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        # The anti-checklist guard: no relationship without a specific requirement + a
        # stated reason. Enforced at construction, not by convention.
        if not value.strip():
            raise ValueError("must be a non-empty, specific statement")
        return value

    @model_validator(mode="after")
    def _state_data_matches_kind(self) -> Self:
        if self.kind is EvidenceKind.EVIDENCED and self.before_after is None:
            raise ValueError(
                "an EVIDENCED relationship must carry before_after data — the "
                "satisfy/violate state is derived from it, never asserted"
            )
        if self.kind is EvidenceKind.NOT_EVIDENCED and self.before_after is not None:
            raise ValueError(
                "a NOT_EVIDENCED (boundary) relationship has no satisfy/violate state, "
                "so it must not carry before_after data"
            )
        return self

    @property
    def evidences(self) -> bool:
        """True iff the event is evidence for this obligation (False = the boundary)."""
        return self.kind is EvidenceKind.EVIDENCED

    @property
    def pre_state(self) -> EvidenceState | None:
        """The pre-patch (VIOLATE) state, or None for a boundary relationship."""
        return self.before_after.pre_state if self.before_after is not None else None

    @property
    def post_state(self) -> EvidenceState | None:
        """The post-patch (SATISFY) state, or None for a boundary relationship."""
        return self.before_after.post_state if self.before_after is not None else None

    @property
    def transition(self) -> tuple[EvidenceState, EvidenceState] | None:
        """The temporal transition (pre → post) — the M2-00 §3 contribution; None at the boundary."""
        if self.before_after is None:
            return None
        return (self.before_after.pre_state, self.before_after.post_state)
