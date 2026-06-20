"""NAT function registrations for the chassis: layer stubs + orchestrator.

Importing this module registers the functions in NAT's global type registry so
`load_workflow` can build them. No business logic and no LLM — each stub only
writes one ledger entry and returns a trivial status.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from nat.builder.builder import Builder
from nat.builder.function_info import FunctionInfo
from nat.cli.register_workflow import register_function

from keystone.assurance.loop import run_assurance_loop
from keystone.assurance.loop_live import live_deps
from keystone.core.ledger import open_ledger

from .config import AssuranceLoopConfig, LayerStubConfig, OrchestratorConfig


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


@register_function(config_type=AssuranceLoopConfig)
async def build_assurance_loop(
    config: AssuranceLoopConfig, builder: Builder
) -> AsyncIterator[Any]:
    """Build the NAT-driven Layer-2 assurance loop (KS-0304).

    NAT's runtime invokes this function; it sequences the existing KS-0301/0303/
    0302 components into the exposed→detected→mapped→patched→verified arc, writing
    each stage to the evidence ledger. No new capability — just orchestration.
    """

    async def _run(message: str) -> str:
        # The loop is fully synchronous (agent, Garak subprocess, and NeMo
        # Guardrails' sync `generate`). Run it in a worker thread so it does not
        # collide with NAT's running event loop (NeMo refuses sync generate inside
        # async). asyncio.to_thread = the idiomatic blocking-in-async bridge.
        ledger = open_ledger()
        deps = live_deps(ledger=ledger, prompt_cap=config.prompt_cap)
        result = await asyncio.to_thread(run_assurance_loop, deps, ledger=ledger)
        return (
            f"exploit before={result.exploit_before} after={result.exploit_after} | "
            f"garak fails before={result.before_fails} after={result.after_fails} | "
            f"remediated={result.remediated} arc_complete={result.arc_complete}"
        )

    yield FunctionInfo.from_fn(_run, description="Keystone Layer-2 assurance loop")
