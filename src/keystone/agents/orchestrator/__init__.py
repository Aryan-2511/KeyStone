"""Chassis orchestrator (orchestration layer).

Importing this package registers the NAT functions and exposes the path to the
workflow config. May depend inward on the deterministic core; the core must not
depend on it.
"""

from pathlib import Path

from .config import LayerStubConfig, OrchestratorConfig
from .functions import build_layer_stub, build_orchestrator

# The packaged NAT workflow config that wires the orchestrator to three stubs.
WORKFLOW_CONFIG = Path(__file__).parent / "workflow.yml"

__all__ = [
    "WORKFLOW_CONFIG",
    "LayerStubConfig",
    "OrchestratorConfig",
    "build_layer_stub",
    "build_orchestrator",
]
