"""UI — Streamlit demo front-end over the workflow and evidence ledger.

The outermost layer; may depend on lower layers. Nothing depends on it.

`modality_view` is the Phase-5 UI's DATA CONTRACT (KS-0203): a deterministic,
tested view-model built by LOOKUP over the crosswalk + guarded phrasing. It does
no rendering and does not import Streamlit, so it is safe to import headless.
"""

from __future__ import annotations

from .modality_view import (
    ControlView,
    JurisdictionMix,
    ModalityMix,
    ObligationView,
    build_modality_view,
    contrast_controls,
)

__all__ = [
    "ControlView",
    "JurisdictionMix",
    "ModalityMix",
    "ObligationView",
    "build_modality_view",
    "contrast_controls",
]
