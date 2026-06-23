"""Regulatory convergence (Movement 2) — seam events as compliance audit evidence.

The evidence model (M2-01): a typed `EvidenceRelationship` binds a seam event to a real,
EXISTING Layer-3 obligation and carries the M2-00 §2 four-part rigor as structure —
obligation + requirement + reason (mandatory) + a satisfy/violate state DERIVED from the
before/after assurance data. The boundary ("not evidenced by this event") is first-class.

This is *defensible technical-compliance evidence reasoning*, NOT a legal or certified
compliance determination (see `EVIDENCE_DISCLAIMER`). Governance/edge logic over the L3
graph + the seam matrix; the deterministic core never imports it (import-linter KEPT).
"""

from __future__ import annotations

from .evidence import (
    EVIDENCE_DISCLAIMER,
    BeforeAfter,
    EvidenceKind,
    EvidenceRelationship,
    EvidenceState,
    ObligationRef,
    SeamEventRef,
    derive_state,
)
from .mappings import (
    REFERENCE_CONTROL_ID,
    REFERENCE_MAPPING,
    REFERENCE_OBLIGATION_ID,
    build_reference_mapping,
)

__all__ = [
    "EVIDENCE_DISCLAIMER",
    "REFERENCE_CONTROL_ID",
    "REFERENCE_MAPPING",
    "REFERENCE_OBLIGATION_ID",
    "BeforeAfter",
    "EvidenceKind",
    "EvidenceRelationship",
    "EvidenceState",
    "ObligationRef",
    "SeamEventRef",
    "build_reference_mapping",
    "derive_state",
]
