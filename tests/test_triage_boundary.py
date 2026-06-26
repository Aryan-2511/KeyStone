"""The memo-blind boundary holds WITH the Triage Agent present (MB-00 §4).

The Triage Agent is a SUPERVISOR: it reads a finding's already-computed signals
(failure_rate, seam_result, severity) as plain values and routes it. The sacred
invariant is that it NEVER reaches into detection — not the L1 FATF detector, not the
seam framework's ``project_financial`` / ``detect``, not the input-rail detector, not
the Garak scanner. It reasons over signals others computed; it does not compute them.

These tests assert (1) the agent module structurally cannot import anything on the
detection path or the attack channel, and (2) the four independence lock points still
hold with BOTH agents (offense Red-Team + supervisor Triage) in the loop. If the
triage agent ever reached into detection to route "more cleverly", the convergence
thesis would collapse — so this is a build-failing gate, not a comment.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

from keystone.agents import red_team
from keystone.agents.red_team import PROBE_CATALOG, profile_observe, run_red_team
from keystone.agents.triage import (
    FindingSeverity,
    SeamClassification,
    TriageSignals,
)
from keystone.agents.triage import triage as run_triage
from keystone.assurance import REGISTERED_PAIRS
from keystone.assurance.framework import (
    FinancialProjection,
    SeamPair,
    financial_projection_for,
)

# The triage SUBMODULE — fetched via importlib because the package namespace binds the
# name ``triage`` to the function (re-exported in keystone.agents.__init__), not the
# module. We scan the module's source file for its imports (the boundary AST check).
triage_module = importlib.import_module("keystone.agents.triage")

# Modules on the DETECTION path / attack channel the supervisor must never reach into.
_FORBIDDEN_IMPORTS = (
    "keystone.core.fatf",  # the FATF engine (memo-blind by design)
    "keystone.core.fatf.engine",  # the detector itself
    "keystone.assurance.framework",  # project_financial / CrimeSide.detect (the lock)
    "keystone.assurance.injection_patterns",  # the input-rail detector
    "keystone.assurance.garak_probe",  # the attack channel / Garak scanner
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


def test_triage_agent_module_has_no_path_to_the_detector() -> None:
    # The supervisor imports nothing on the detection path: it routes over signals
    # others computed, and structurally cannot recompute or reach into them (MB-00 §4).
    imports = _imported_modules(Path(triage_module.__file__))
    for forbidden in _FORBIDDEN_IMPORTS:
        assert forbidden not in imports, (
            f"the Triage Agent must not import {forbidden!r} — it is a SUPERVISOR that "
            f"reads already-computed signals and must have no path to the detector or "
            f"the attack channel (MB-00 §4)"
        )
    # It imports nothing from the deterministic core or the assurance edge at all —
    # it carries its OWN value enums (parity-tested) so the boundary is structural.
    assert not any(m.startswith("keystone.core") for m in imports)
    assert not any(m.startswith("keystone.assurance") for m in imports)


def test_neither_agent_reaches_the_detector() -> None:
    # The boundary holds for BOTH agents present — the offense worker AND the
    # supervisor are each forbidden the detection path (the multi-agent boundary).
    for agent_module in (red_team, triage_module):
        imports = _imported_modules(Path(agent_module.__file__))
        assert "keystone.assurance.framework" not in imports
        assert not any(m.startswith("keystone.core.fatf") for m in imports)


@pytest.mark.parametrize("pair", REGISTERED_PAIRS, ids=lambda p: p.pair_id)
def test_independence_holds_with_both_agents_present(pair: SeamPair) -> None:
    # Run BOTH agents — the offense (Red-Team) AND the supervisor (Triage) — then
    # assert the detector still receives a memo-blind projection for every registered
    # pair. Neither agent changes the independence guarantee (locks at framework.py
    # project_financial / detect).
    run_red_team(profile_observe(red_team.RECORDED_DEFENSE_PROFILE))
    run_triage(
        TriageSignals(
            failure_rate=0.83,
            seam_result=SeamClassification.CLEAN,
            severity=FindingSeverity.HIGH,
        )
    )
    projection = financial_projection_for(pair)
    assert isinstance(projection, FinancialProjection)
    assert all(txn.memo == "" for txn in projection.transactions)


def test_triage_signals_carry_no_attack_channel_content() -> None:
    # The supervisor's whole input is three abstract signals — a rate, a seam class, a
    # severity. None of the attack channel (probe names) rides in its observed state,
    # so a triage decision can never leak the attack vocabulary back toward detection.
    every_probe = {p for fam in PROBE_CATALOG.values() for p in fam}
    decision = run_triage(
        TriageSignals(
            failure_rate=0.5,
            seam_result=SeamClassification.OPEN,
            severity=FindingSeverity.MEDIUM,
        )
    )
    blob = decision.model_dump_json()
    assert not any(probe in blob for probe in every_probe)
