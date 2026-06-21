"""Integration / demo layer (Phase 5).

The typed `RunResult` — the single contract the Phase-5 front-end renders from —
and the runner that builds it from a real Layer-1 arc, plus save/load for offline
replay. Composes the deterministic core and the assurance edge; the core never
imports this layer (import-linter KEPT).
"""

from __future__ import annotations

from .run_result import (
    RUN_RESULT_SCHEMA_VERSION,
    AiSecurityView,
    ArcView,
    FinancialCrimeView,
    RegulatoryMappingView,
    ReportView,
    RunResult,
    SeamBindingView,
    SeamTransactionView,
)
from .runner import (
    DEFAULT_RUN_PATH,
    RunResultError,
    build_run_result,
    load_run_result,
    run_json_path,
    save_run_result,
)

__all__ = [
    "DEFAULT_RUN_PATH",
    "RUN_RESULT_SCHEMA_VERSION",
    "AiSecurityView",
    "ArcView",
    "FinancialCrimeView",
    "RegulatoryMappingView",
    "ReportView",
    "RunResult",
    "RunResultError",
    "SeamBindingView",
    "SeamTransactionView",
    "build_run_result",
    "load_run_result",
    "run_json_path",
    "save_run_result",
]
