"""Entry point: run the chassis NAT workflow once, end-to-end.

    python -m keystone.agents.run

Importing the orchestrator package registers its NAT functions; we then load the
packaged workflow config and invoke it. The ledger location comes from
KEYSTONE_LEDGER_DB (see keystone.core.ledger).
"""

from __future__ import annotations

import asyncio

from nat.runtime.loader import load_workflow

from keystone.agents import orchestrator
from keystone.core.ledger import open_ledger


async def run_once(message: str = "run") -> str:
    """Run the workflow a single time and return the orchestrator's status."""
    async with (
        load_workflow(orchestrator.WORKFLOW_CONFIG) as session,
        session.run(message) as runner,
    ):
        return str(await runner.result(to_type=str))


async def run_milestone(message: str = "run") -> str:
    """Run the KS-0304 assurance loop end-to-end via NAT and return the summary."""
    async with (
        load_workflow(orchestrator.ASSURANCE_WORKFLOW_CONFIG) as session,
        session.run(message) as runner,
    ):
        return str(await runner.result(to_type=str))


def main() -> None:
    result = asyncio.run(run_once())
    ledger = open_ledger()
    print(f"workflow result: {result}")
    print(f"ledger entries: {len(ledger.all())}  chain_ok: {ledger.verify_chain()}")


def main_milestone() -> None:
    """`make milestone` entry point: NAT-orchestrated assurance loop + chain summary."""
    result = asyncio.run(run_milestone())
    ledger = open_ledger()
    arc = [
        e.payload.get("stage")
        for e in ledger.all()
        if e.action == "assurance_loop_stage"
    ]
    print(f"assurance loop: {result}")
    print(f"ledger arc: {' -> '.join(str(s) for s in arc)}")
    print(f"ledger entries: {len(ledger.all())}  chain_ok: {ledger.verify_chain()}")


async def run_layer1(message: str = "run") -> str:
    """Run the KS-0405 Layer-1 milestone arc end-to-end via NAT and return the summary."""
    async with (
        load_workflow(orchestrator.LAYER1_WORKFLOW_CONFIG) as session,
        session.run(message) as runner,
    ):
        return str(await runner.result(to_type=str))


def main_layer1_milestone() -> None:
    """`make layer1-milestone` entry: NAT-orchestrated Layer-1 arc + chain summary."""
    result = asyncio.run(run_layer1())
    ledger = open_ledger()
    arc = [
        e.payload.get("stage")
        for e in ledger.all()
        if e.action == "layer1_milestone_stage"
    ]
    print(f"layer-1 milestone: {result}")
    print(f"ledger arc: {' -> '.join(str(s) for s in arc)}")
    print(f"ledger entries: {len(ledger.all())}  chain_ok: {ledger.verify_chain()}")


if __name__ == "__main__":
    main()
