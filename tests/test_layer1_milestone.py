"""The Layer-1 milestone (KS-0405) — closing the seam to L2, NAT-orchestrated.

The FAST gate exercises the arc's DETERMINISTIC spine over a canned narrative — no
Ollama, no network — and proves the arc is whole and ordered, that the SEAM stage
binds the FATF-flagged transaction to the SAME canonical MEMO_INJECTION_SIGNATURE
Layer 2 found+patched (referenced, not re-run), and that a chain missing/out-of-
order a stage FAILS. It also validates the NAT workflow config. The full live arc
via NAT is the `-m slow` + `@milestone` test.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx
import pytest

from keystone.agents.orchestrator import LAYER1_WORKFLOW_CONFIG
from keystone.agents.orchestrator.config import Layer1MilestoneConfig
from keystone.agents.run import run_layer1
from keystone.assurance import MEMO_INJECTION_SIGNATURE
from keystone.assurance import layer1_milestone as milestone
from keystone.assurance.layer1_milestone import (
    ARC,
    MILESTONE_ACTION,
    Layer1MilestoneError,
    Layer1Stage,
    assert_layer1_arc,
    run_layer1_milestone,
)
from keystone.core.ledger import Ledger
from keystone.core.reporting import ReportFacts, template_narrative
from keystone.llm.report_narrative import GuardedNarrative


def _faithful(facts: ReportFacts) -> GuardedNarrative:
    """A canned faithful narrative (the deterministic template) for the fast spine."""
    return GuardedNarrative(text=template_narrative(facts), fell_back=False)


def _stages(ledger: Ledger) -> list[str]:
    return [e.payload["stage"] for e in ledger.all() if e.action == MILESTONE_ACTION]


# --- the deterministic spine: arc runs in order, chain valid ------------------


def test_arc_runs_in_order(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    result = run_layer1_milestone(narrate=_faithful, ledger=ledger)

    assert tuple(Layer1Stage(s) for s in _stages(ledger)) == ARC
    assert result.fatf_typology == "STRUCTURING"
    assert result.l2_signature == MEMO_INJECTION_SIGNATURE.name
    assert result.arc_complete is True
    assert ledger.verify_chain() is True


def test_seam_stage_binds_the_flagged_tx_to_the_l2_signature(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    result = run_layer1_milestone(narrate=_faithful, ledger=ledger)
    by_stage = {
        e.payload["stage"]: e.payload
        for e in ledger.all()
        if e.action == MILESTONE_ACTION
    }
    # The FATF stage flagged the seam transaction (financial, memo-blind)...
    assert by_stage["detected"]["implicates_seam_tx"] is True
    assert result.seam_transaction_id in by_stage["detected"]["transaction_ids"]
    # ...and the seam stage ties THAT SAME tx to the L2 signature, referencing
    # (not re-running) the proven Layer-2 finding.
    seam = by_stage["seam_bound"]
    assert seam["transaction_id"] == result.seam_transaction_id
    assert seam["l2_signature"] == MEMO_INJECTION_SIGNATURE.name
    assert "not re-run" in seam["l2_reference"]


def test_reported_stage_carries_a_finnet_report(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    run_layer1_milestone(narrate=_faithful, ledger=ledger)
    reported = next(
        e.payload for e in ledger.all() if e.payload.get("stage") == "reported"
    )
    assert reported["report_format"] == "FINNET"
    assert reported["finnet_report"]["report_type"] == "STR"
    assert reported["narrative_fell_back"] is False


def test_narrative_fall_back_propagates(tmp_path: Path) -> None:
    def _liar(facts: ReportFacts) -> GuardedNarrative:
        return GuardedNarrative(text=template_narrative(facts), fell_back=True)

    ledger = Ledger(tmp_path / "l.db")
    result = run_layer1_milestone(narrate=_liar, ledger=ledger)
    assert result.narrative_fell_back is True


# --- the milestone "assert the arc" check rejects incomplete / disordered -----


def _write_stages(ledger: Ledger, stages: list[str]) -> None:
    for stage in stages:
        ledger.append(
            agent="x", layer="L1", action=MILESTONE_ACTION, payload={"stage": stage}
        )


def test_arc_check_rejects_missing_stage(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    _write_stages(ledger, ["ingested", "detected", "reported", "signed"])  # no seam
    assert assert_layer1_arc(ledger) is False


def test_arc_check_rejects_out_of_order(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    _write_stages(ledger, ["detected", "ingested", "seam_bound", "reported", "signed"])
    assert assert_layer1_arc(ledger) is False


def test_milestone_fails_loud_if_signature_stops_resolving(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Drift guard: if the seam tx stopped carrying the L2 signature, the milestone
    # fails loudly instead of silently passing.
    monkeypatch.setattr(milestone, "resolve_signature", lambda _memo: None)
    with pytest.raises(Layer1MilestoneError, match="did not resolve"):
        run_layer1_milestone(narrate=_faithful, ledger=Ledger(tmp_path / "l.db"))


# --- NAT workflow config validates without a live run -------------------------


def test_nat_layer1_workflow_config_loads() -> None:
    text = LAYER1_WORKFLOW_CONFIG.read_text(encoding="utf-8")
    assert "_type: keystone_layer1_milestone" in text
    config = Layer1MilestoneConfig(signer="x@y")
    assert config.signer == "x@y"


# --- the live milestone: full arc via NAT (slow; skips cleanly) ---------------


def _ollama_up() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2.0)
    except httpx.HTTPError:
        return False
    return True


@pytest.mark.slow
@pytest.mark.milestone
def test_live_layer1_arc_via_nat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if not _ollama_up():
        pytest.skip("Ollama not running")

    db = tmp_path / "milestone.db"
    monkeypatch.setenv("KEYSTONE_LEDGER_DB", str(db))
    asyncio.run(run_layer1())

    ledger = Ledger(db)
    assert assert_layer1_arc(ledger) is True  # full ordered arc, hash-valid
    payloads = {
        e.payload["stage"]: e.payload
        for e in ledger.all()
        if e.action == MILESTONE_ACTION
    }
    # The seam binds the L1 fraud to the L2 signature.
    assert payloads["seam_bound"]["l2_signature"] == MEMO_INJECTION_SIGNATURE.name
    reported = payloads["reported"]
    print(
        f"\nLIVE Layer-1 arc: fraud={payloads['ingested']['seam_transaction_id']} "
        f"-> L2 sig={payloads['seam_bound']['l2_signature']} "
        f"signed_by={payloads['signed']['signed_by']} "
        f"fell_back={reported['narrative_fell_back']}"
    )
    assert payloads["signed"]["status"] == "SIGNED"
