"""Integration / demo layer (Phase 5).

The typed `RunResult` — the single contract the Phase-5 front-end renders from —
and the runner that builds it from a real Layer-1 arc, plus save/load for offline
replay. Composes the deterministic core and the assurance edge; the core never
imports this layer (import-linter KEPT).
"""

from __future__ import annotations

from .convergence import build_convergence_view
from .matrix import build_matrix_view
from .red_team import build_red_team_view
from .run_result import (
    RUN_RESULT_SCHEMA_VERSION,
    AiSecurityView,
    ArcView,
    ConvergenceMappingView,
    ConvergenceView,
    FinancialCrimeView,
    MatrixPairView,
    MatrixView,
    RedTeamProbeView,
    RedTeamView,
    RegulatoryMappingView,
    ReportView,
    RunResult,
    SeamBindingView,
    SeamTransactionView,
)
from .runner import (
    DEFAULT_RUN_PATH,
    RECORDED_RUN_PATH,
    RunResultError,
    build_run_result,
    load_recorded_run,
    load_run_result,
    recorded_run_path,
    run_json_path,
    save_run_result,
)

__all__ = [
    "DEFAULT_RUN_PATH",
    "RECORDED_RUN_PATH",
    "RUN_RESULT_SCHEMA_VERSION",
    "AiSecurityView",
    "ArcView",
    "ConvergenceMappingView",
    "ConvergenceView",
    "FinancialCrimeView",
    "MatrixPairView",
    "MatrixView",
    "RedTeamProbeView",
    "RedTeamView",
    "RegulatoryMappingView",
    "ReportView",
    "RunResult",
    "RunResultError",
    "SeamBindingView",
    "SeamTransactionView",
    "build_convergence_view",
    "build_matrix_view",
    "build_red_team_view",
    "build_run_result",
    "load_recorded_run",
    "load_run_result",
    "recorded_run_path",
    "run_json_path",
    "save_run_result",
]
