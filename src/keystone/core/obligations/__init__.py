"""Curated regulatory obligation graph (deterministic core).

Public surface: the `Obligation` and `Citation` models, the `Instrument`,
`Modality` and `Jurisdiction` enums, the fail-loud `load_obligations` loader,
its `ObligationLoadError`, and the packaged `DATA_PATH`. No LLM or network deps
(ADR-0008); the schema and storage are locked by ADR-0012.
"""

from __future__ import annotations

from .loader import DATA_PATH, ObligationLoadError, load_obligations
from .models import Citation, Instrument, Jurisdiction, Modality, Obligation

__all__ = [
    "DATA_PATH",
    "Citation",
    "Instrument",
    "Jurisdiction",
    "Modality",
    "Obligation",
    "ObligationLoadError",
    "load_obligations",
]
