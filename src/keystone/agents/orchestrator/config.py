"""NAT config models for the chassis orchestrator and its layer stubs.

The class `name=` becomes the YAML `_type` discriminator (see workflow.yml).
These subclass NeMo Agent Toolkit's `FunctionBaseConfig`, which is untyped
upstream — hence the scoped mypy override for this package (see ADR-0010).
"""

from __future__ import annotations

from nat.data_models.function import FunctionBaseConfig


class LayerStubConfig(FunctionBaseConfig, name="keystone_layer_stub"):
    """A stub for one mesh layer; writes a single ledger entry when invoked."""

    layer: str


class OrchestratorConfig(FunctionBaseConfig, name="keystone_orchestrator"):
    """Fans out to the named layer-stub functions, in order."""

    layers: list[str]


class AssuranceLoopConfig(FunctionBaseConfig, name="keystone_assurance_loop"):
    """Drives the end-to-end Layer-2 assurance loop (KS-0304).

    `prompt_cap` bounds the two live Garak scans (before/after the patch).
    """

    prompt_cap: int = 12
