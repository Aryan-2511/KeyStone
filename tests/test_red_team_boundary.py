"""The memo-blind boundary holds WITH the Red-Team Agent present (MA-00 §5).

The agent lives on the OFFENSE side: it reads and reasons over the attack channel
(injection probes) — that is its job. The sacred invariant is that it has NO path
to the crime detector: nothing the agent observes can reach a memo-blind FATF
detector except through the typed projection the framework already enforces. These
tests assert (1) the agent module structurally cannot import the detector, and
(2) the four independence lock points still hold with the agent in the loop.

If an "agent that reads the attack to be smarter" ever touched detection, the
convergence thesis would collapse — so this is a build-failing gate, not a comment.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from keystone.agents import red_team
from keystone.agents.red_team import PROBE_CATALOG, profile_observe, run_red_team
from keystone.assurance import REGISTERED_PAIRS
from keystone.assurance.framework import (
    FinancialProjection,
    SeamPair,
    financial_projection_for,
)

# Modules on the DETECTION path the offense agent must never reach into.
_FORBIDDEN_IMPORTS = (
    "keystone.core.fatf",  # the FATF engine (memo-blind by design)
    "keystone.assurance.framework",  # project_financial / CrimeSide.detect (the lock)
    "keystone.assurance.injection_patterns",  # the input-rail detector
)


def _imported_modules(source: Path) -> set[str]:
    """Every module name the source file imports (absolute form)."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            names.add(node.module)
    return names


def test_agent_module_has_no_path_to_the_detector() -> None:
    # Lock #4 (feasibility): the agent literally cannot be wired into the detector,
    # because it imports nothing on the detection path. The offense reaches Garak
    # (the scan), never the crime side.
    imports = _imported_modules(Path(red_team.__file__))
    for forbidden in _FORBIDDEN_IMPORTS:
        assert forbidden not in imports, (
            f"the Red-Team Agent must not import {forbidden!r} — it is on the OFFENSE "
            f"side and must have no path to the memo-blind detector (MA-00 §5)"
        )
    # It imports nothing from the deterministic core at all.
    assert not any(m.startswith("keystone.core") for m in imports)


@pytest.mark.parametrize("pair", REGISTERED_PAIRS, ids=lambda p: p.pair_id)
def test_independence_holds_with_the_agent_present(pair: SeamPair) -> None:
    # Run the agent (offense) FIRST, then assert the detector still receives a
    # memo-blind projection for every registered pair — the agent changes nothing
    # about the independence guarantee (locks at framework.py project_financial/detect).
    run_red_team(profile_observe(red_team.RECORDED_DEFENSE_PROFILE))
    projection = financial_projection_for(pair)
    assert isinstance(projection, FinancialProjection)
    assert all(txn.memo == "" for txn in projection.transactions)


def test_agent_attack_probes_never_appear_in_a_financial_projection() -> None:
    # The agent's whole vocabulary is the attack channel (probe names). None of it
    # may ride into the financial projection the detector sees — the channels are
    # disjoint by construction.
    every_probe = {p for fam in PROBE_CATALOG.values() for p in fam}
    for pair in REGISTERED_PAIRS:
        projection = financial_projection_for(pair)
        for txn in projection.transactions:
            blob = txn.model_dump_json()
            assert not any(probe in blob for probe in every_probe)
