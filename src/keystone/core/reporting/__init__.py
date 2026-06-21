"""Regulator report generation (deterministic core, Layer 1 — KS-0404).

Public surface: the `ReportFacts` system-of-record + `assemble_facts`, the
deterministic faithfulness guard (`template_narrative`, `narrative_is_faithful`),
the `Report` object with its draft/signed status, the FINnet/goAML format adapters
(`render`, `to_finnet`, `to_goaml`), `sign_off`, and `record_report`. The LLM edge
phrases ONLY the narrative; facts and the guard are core. No LLM/network deps
(ADR-0008).
"""

from __future__ import annotations

from .facts import (
    ReportAssemblyError,
    ReportFacts,
    assemble_facts,
    narrative_is_faithful,
    template_narrative,
)
from .report import (
    LEDGER_AGENT,
    LEDGER_LAYER,
    Report,
    ReportFormat,
    ReportStatus,
    record_report,
    render,
    sign_off,
    to_finnet,
    to_goaml,
)

__all__ = [
    "LEDGER_AGENT",
    "LEDGER_LAYER",
    "Report",
    "ReportAssemblyError",
    "ReportFacts",
    "ReportFormat",
    "ReportStatus",
    "assemble_facts",
    "narrative_is_faithful",
    "record_report",
    "render",
    "sign_off",
    "template_narrative",
    "to_finnet",
    "to_goaml",
]
