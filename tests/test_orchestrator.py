"""Milestone integration test for the chassis (KS-0101).

Runs the real NAT workflow end-to-end (no LLM, no network) and asserts the mesh
wrote exactly three layer entries and the evidence chain verifies.
"""

import asyncio
from pathlib import Path

import pytest

from keystone.agents.run import run_once
from keystone.core.ledger import Ledger

LAYERS = {"layer1", "layer2", "layer3"}


@pytest.mark.milestone
def test_chassis_runs_three_layers_and_chain_verifies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    db = tmp_path / "ledger.db"
    monkeypatch.setenv("KEYSTONE_LEDGER_DB", str(db))

    result = asyncio.run(run_once())
    assert "layer1" in result and "layer3" in result

    ledger = Ledger(db)
    layer_entries = [e for e in ledger.all() if e.layer in LAYERS]
    assert len(layer_entries) == 3
    assert {e.layer for e in layer_entries} == LAYERS
    assert ledger.verify_chain() is True
