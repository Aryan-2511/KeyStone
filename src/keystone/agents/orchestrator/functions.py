"""NAT function registrations for the chassis: layer stubs + orchestrator.

Importing this module registers the functions in NAT's global type registry so
`load_workflow` can build them. No business logic and no LLM — each stub only
writes one ledger entry and returns a trivial status.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function

from keystone.core.ledger import open_ledger

from .config import LayerStubConfig, OrchestratorConfig


@register_function(config_type=LayerStubConfig)
async def build_layer_stub(
    config: LayerStubConfig, builder: Builder
) -> AsyncIterator[Any]:
    """Build a layer stub that records its one ledger entry."""

    async def _run(message: str) -> str:
        open_ledger().append(
            agent=f"{config.layer}_stub",
            layer=config.layer,
            action="stub_invoked",
            payload={"note": "synthetic chassis stub"},
        )
        return f"{config.layer}: ok"

    yield FunctionInfo.from_fn(_run, description=f"Chassis stub for {config.layer}")


@register_function(config_type=OrchestratorConfig)
async def build_orchestrator(
    config: OrchestratorConfig, builder: Builder
) -> AsyncIterator[Any]:
    """Build the orchestrator that fans out to the configured layer stubs."""

    async def _run(message: str) -> str:
        statuses: list[str] = []
        for name in config.layers:
            stub = await builder.get_function(name)
            result = await stub.ainvoke(message, to_type=str)
            statuses.append(str(result))
        return " | ".join(statuses)

    yield FunctionInfo.from_fn(_run, description="Keystone chassis orchestrator")
