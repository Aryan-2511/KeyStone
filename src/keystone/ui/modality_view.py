"""Modality-contrast view-model (KS-0203) — the Phase-5 UI's data contract.

This is presentation-layer DATA SHAPING, not rendering. There is no Streamlit,
no HTML, no layout here — that is deferred to Phase 5. The module READS what the
deterministic core already produced (the KS-0202 crosswalk: control → its
obligations, with `enforcement_modality` preserved) and the GUARDED LLM-edge
phrasing (KS-0204/0206 `phrase_summary` → `PhrasedSummary`), and assembles a
typed view-model by LOOKUP. It recomputes nothing: controls and the crosswalk
JOIN are consumed as given.

Because it calls the LLM-edge phrasing, the view-model itself lives in the edge
layer (ADR-0008) — `keystone.ui`, the outermost layer that may depend on the
core and the LLM seam but that nothing depends on. The deterministic core never
imports this. Building the view leaves all core data byte-identical: phrasing
reads `summary` and returns derived text; nothing is written back.

The contrast is the headline: a single control that carries BOTH a HARD_LAW
obligation (an EU article) AND a SELF_CERTIFICATION obligation (an RBI sutra) is
the demo's money shot, surfaced as the first-class `has_modality_contrast` flag.
"""

from __future__ import annotations

import enum
from collections.abc import Sequence
from dataclasses import dataclass

from keystone.core.controls import ControlMapping
from keystone.core.controls.models import Control
from keystone.core.obligations import Citation, Jurisdiction, Modality
from keystone.llm import PhrasedSummary, phrase_summary
from keystone.llm.inference import Backend


class ModalityMix(enum.StrEnum):
    """Categorical summary of the modalities present under one control.

    `BOTH` is the contrast case — a control spanning hard law and
    self-certification. (`Modality` itself has only the two atomic values.)
    """

    HARD_LAW = "HARD_LAW"
    SELF_CERTIFICATION = "SELF_CERTIFICATION"
    BOTH = "BOTH"


class JurisdictionMix(enum.StrEnum):
    """Categorical summary of the jurisdictions present under one control."""

    EU = "EU"
    INDIA = "INDIA"
    BOTH = "BOTH"


@dataclass(frozen=True)
class ObligationView:
    """One obligation as the UI will show it under a control.

    `display_summary` is the GUARDED phrasing output (`PhrasedSummary.text`):
    the reworded text when faithful, or the curated source verbatim on fallback.
    `fell_back` is preserved so Phase 5 can badge the latter as authoritative.
    The structured `citation` is carried whole so rendering can choose how to
    show the provision / instrument / source link.
    """

    id: str
    citation: Citation
    jurisdiction: Jurisdiction
    modality: Modality
    display_summary: str
    fell_back: bool


@dataclass(frozen=True)
class ControlView:
    """One control, its obligations, and the modality/jurisdiction contrast.

    `modalities` and `jurisdictions` are the raw sets present among the
    obligations (preserved from the crosswalk); `modality_mix` /
    `jurisdiction_mix` are the categorical summaries derived from them.
    `has_modality_contrast` is the first-class headline flag.
    """

    control: Control
    obligations: tuple[ObligationView, ...]
    modalities: frozenset[Modality]
    jurisdictions: frozenset[Jurisdiction]

    @property
    def has_modality_contrast(self) -> bool:
        """True iff this control carries BOTH hard law AND self-certification."""
        return (
            Modality.HARD_LAW in self.modalities
            and Modality.SELF_CERTIFICATION in self.modalities
        )

    @property
    def modality_mix(self) -> ModalityMix | None:
        """HARD_LAW only / SELF_CERTIFICATION only / BOTH; None if no obligations."""
        has_hard = Modality.HARD_LAW in self.modalities
        has_self = Modality.SELF_CERTIFICATION in self.modalities
        if has_hard and has_self:
            return ModalityMix.BOTH
        if has_hard:
            return ModalityMix.HARD_LAW
        if has_self:
            return ModalityMix.SELF_CERTIFICATION
        return None

    @property
    def jurisdiction_mix(self) -> JurisdictionMix | None:
        """EU only / INDIA only / BOTH; None if no obligations."""
        has_eu = Jurisdiction.EU in self.jurisdictions
        has_india = Jurisdiction.INDIA in self.jurisdictions
        if has_eu and has_india:
            return JurisdictionMix.BOTH
        if has_eu:
            return JurisdictionMix.EU
        if has_india:
            return JurisdictionMix.INDIA
        return None


def build_modality_view(
    crosswalk: Sequence[ControlMapping],
    *,
    backend: Backend | None = None,
) -> list[ControlView]:
    """Assemble the view-model from the KS-0202 crosswalk by LOOKUP.

    For each `ControlMapping` (already ordered and de-duplicated by the
    crosswalk), build one `ControlView`: its obligations become `ObligationView`s
    whose `display_summary` is the GUARDED `phrase_summary` output. Order is
    inherited verbatim from the crosswalk — controls in `controls` order,
    obligations sorted by id — so the same inputs always produce an identical
    view-model.

    `backend` is the injectable inference seam (the same one `phrase_summary`
    uses): the fast test gate passes a fake backend so no live NIM is touched.
    Building the view never mutates any obligation or core data file.
    """
    views: list[ControlView] = []
    for mapping in crosswalk:
        obligation_views: list[ObligationView] = []
        for obligation in mapping.obligations:
            phrased: PhrasedSummary = phrase_summary(obligation, backend=backend)
            obligation_views.append(
                ObligationView(
                    id=obligation.id,
                    citation=obligation.citation,
                    jurisdiction=obligation.jurisdiction,
                    modality=obligation.enforcement_modality,
                    display_summary=phrased.text,
                    fell_back=phrased.fell_back,
                )
            )
        jurisdictions = frozenset(o.jurisdiction for o in obligation_views)
        views.append(
            ControlView(
                control=mapping.control,
                obligations=tuple(obligation_views),
                modalities=mapping.modalities,
                jurisdictions=jurisdictions,
            )
        )
    return views


def contrast_controls(views: Sequence[ControlView]) -> list[ControlView]:
    """Filter the view-model down to the modality-contrast controls.

    A convenience over the built view-model (not separate logic): returns, in the
    same order, only the controls where `has_modality_contrast` is true — the
    demo highlights (governance + transparency spanning an EU article and an RBI
    sutra).
    """
    return [view for view in views if view.has_modality_contrast]
