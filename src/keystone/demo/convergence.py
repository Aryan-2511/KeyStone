"""Build the regulatory-convergence result from REGISTERED_MAPPINGS (M2-0n).

The convergence block of the `RunResult` is DERIVED from
`keystone.convergence.REGISTERED_MAPPINGS` — the single source of truth — so adding a
mapping makes it appear in the result (and the hero) with nothing hardcoded. This module
holds only the presentation derivation: plain-language obligation labels (a judge won't
know the instrument names cold) and the modality translation. No re-derivation of the
satisfy/violate state — that comes already DERIVED from the evidence model; here we read
it.

Boundary: lives in `keystone.demo` (it draws on the convergence edge); the core never
imports it (import-linter KEPT).
"""

from __future__ import annotations

from keystone.convergence import (
    EVIDENCE_DISCLAIMER,
    REGISTERED_MAPPINGS,
    EvidenceRelationship,
)

from .run_result import ConvergenceMappingView, ConvergenceView

# Plain-language instrument names for the obligation labels (the figure translates ids).
_INSTRUMENT_LABELS: dict[str, str] = {
    "EU_AI_ACT": "EU AI Act",
    "DORA": "DORA",
    "DPDP_ACT": "DPDP Act",
    "DPDP_RULES_2025": "DPDP Rules 2025",
    "RBI_GUIDANCE": "RBI FREE-AI",
    "PMLA_FIU_IND": "PMLA / FIU-IND",
}

_MODALITY_LABELS: dict[str, str] = {
    "HARD_LAW": "hard law",
    "SELF_CERTIFICATION": "advisory",
}


def _mapping_view(m: EvidenceRelationship) -> ConvergenceMappingView:
    """Project one evidence relationship into the typed view (reading its DERIVED state)."""
    ob = m.obligation
    instrument = _INSTRUMENT_LABELS.get(ob.instrument, ob.instrument)
    label = f"{instrument} · {ob.provision} — {ob.title}"
    ba = m.before_after
    return ConvergenceMappingView(
        obligation_id=ob.id,
        obligation_label=label,
        jurisdiction=ob.jurisdiction,
        modality=ob.modality,
        modality_label=_MODALITY_LABELS.get(ob.modality, ob.modality.lower()),
        requirement=m.requirement,
        reason=m.reason,
        kind=m.kind.value,
        pre_state=m.pre_state.value if m.pre_state is not None else None,
        post_state=m.post_state.value if m.post_state is not None else None,
        before_fails=ba.before_fails if ba is not None else None,
        after_fails=ba.after_fails if ba is not None else None,
        prompt_cap=ba.prompt_cap if ba is not None else None,
    )


def build_convergence_view() -> ConvergenceView:
    """Assemble the `ConvergenceView` from REGISTERED_MAPPINGS (derived, never hardcoded)."""
    views = [_mapping_view(m) for m in REGISTERED_MAPPINGS]
    evidenced = [v for v in views if v.kind == "EVIDENCED"]
    return ConvergenceView(
        mappings=tuple(views),
        evidenced_count=len(evidenced),
        boundary_count=sum(1 for v in views if v.kind == "NOT_EVIDENCED"),
        hard_law_count=sum(1 for v in evidenced if v.modality == "HARD_LAW"),
        advisory_count=sum(1 for v in evidenced if v.modality == "SELF_CERTIFICATION"),
        jurisdictions=tuple(dict.fromkeys(v.jurisdiction for v in views)),
        disclaimer=EVIDENCE_DISCLAIMER,
    )
