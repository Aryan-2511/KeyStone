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


def main() -> None:
    result = asyncio.run(run_once())
    ledger = open_ledger()
    print(f"workflow result: {result}")
    print(f"ledger entries: {len(ledger.all())}  chain_ok: {ledger.verify_chain()}")


if __name__ == "__main__":
    main()
