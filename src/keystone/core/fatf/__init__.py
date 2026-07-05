"""FATF typology detection engine (deterministic core, Layer 1 — KS-0402).

Public surface: the `Typology`/`Severity` enums and `Finding` model, the
`FatfThresholds` (named, configurable), the memo-BLIND `detect` engine, and
`record_findings` (findings → evidence ledger). Detection uses financial signals
only and never reads `Transaction.memo` — the invariant that keeps the KS-0403
seam's two detections independent. No LLM or network deps (ADR-0008).
"""

from __future__ import annotations

from .engine import (
    DEFAULT_THRESHOLDS,
    FLAGGED_DESTINATIONS,
    LEDGER_ACTION,
    LEDGER_AGENT,
    LEDGER_LAYER,
    STRICT_THRESHOLDS,
    FatfThresholds,
    detect,
    record_findings,
)
from .models import Finding, Severity, Typology

__all__ = [
    "DEFAULT_THRESHOLDS",
    "FLAGGED_DESTINATIONS",
    "LEDGER_ACTION",
    "LEDGER_AGENT",
    "LEDGER_LAYER",
    "STRICT_THRESHOLDS",
    "FatfThresholds",
    "Finding",
    "Severity",
    "Typology",
    "detect",
    "record_findings",
]
