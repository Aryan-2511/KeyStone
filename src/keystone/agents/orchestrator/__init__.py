"""Chassis orchestrator (orchestration layer).

Importing this package registers the NAT functions and exposes the path to the
workflow config. May depend inward on the deterministic core; the core must not
depend on it.
"""

from pathlib import Path

from .config import AssuranceLoopConfig, LayerStubConfig, OrchestratorConfig
from .functions import build_assurance_loop, build_layer_stub, build_orchestrator

# The packaged NAT workflow config that wires the orchestrator to three stubs.
WORKFLOW_CONFIG = Path(__file__).parent / "workflow.yml"
# The KS-0304 milestone workflow: NAT drives the end-to-end assurance loop.
ASSURANCE_WORKFLOW_CONFIG = Path(__file__).parent / "assurance_workflow.yml"

__all__ = [
    "ASSURANCE_WORKFLOW_CONFIG",
    "WORKFLOW_CONFIG",
    "AssuranceLoopConfig",
    "LayerStubConfig",
    "OrchestratorConfig",
    "build_assurance_loop",
    "build_layer_stub",
    "build_orchestrator",
]
