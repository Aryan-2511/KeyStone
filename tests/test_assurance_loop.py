"""Tests for the Layer-2 AI Assurance Loop (KS-0304).

The FAST gate exercises the loop's DETERMINISTIC spine over canned stage results
— NO Garak, NO Ollama, NO network — and proves the arc is whole and ordered: all
five stages run in sequence, each writes its ledger entry, and a chain missing a
stage or out of order FAILS the milestone check. It also validates the NAT
workflow config without a live run. The full live loop via NAT is the
`-m slow` + `@milestone` test.
"""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import httpx
import pytest

from keystone.agents.orchestrator import ASSURANCE_WORKFLOW_CONFIG
from keystone.agents.orchestrator.config import AssuranceLoopConfig
from keystone.agents.run import run_milestone
from keystone.assurance.agent import AgentRun, Transaction, TransferIntent
from keystone.assurance.garak_probe import parse_report
from keystone.assurance.loop import (
    ARC,
    LOOP_ACTION,
    AssuranceLoopError,
    LoopDeps,
    LoopStage,
    assert_assurance_arc,
    run_assurance_loop,
)
from keystone.assurance.signature import CANONICAL_MEMO_EXPLOIT
from keystone.core.ledger import Ledger
from keystone.llm.inference import ToolCall

_FIXTURES = Path(__file__).parent / "fixtures" / "garak"
VULNERABLE = parse_report(_FIXTURES / "latentinjection_vulnerable.report.jsonl")
GUARDED = parse_report(_FIXTURES / "latentinjection_guarded.report.jsonl")

_EXPLOIT_TXN = Transaction(amount=200.0, sender="Bob", memo=CANONICAL_MEMO_EXPLOIT.memo)
_EXPOSED = AgentRun(
    transaction=_EXPLOIT_TXN,
    tool_calls=(ToolCall(name="initiate_transfer", arguments={"amount": 9999}),),
    transfer_intents=(
        TransferIntent(
            amount=9999.0,
            recipient="ATTACKER-999",
            triggered_by=_EXPLOIT_TXN.memo,
            source_field="memo",
        ),
    ),
)
_GUARDED_RUN = AgentRun(
    transaction=_EXPLOIT_TXN, tool_calls=(), transfer_intents=(), blocked=True
)


def _canned_deps() -> LoopDeps:
    return LoopDeps(
        expose=lambda: _EXPOSED,
        detect=lambda: VULNERABLE,
        rescan=lambda: GUARDED,
        reverify=lambda: _GUARDED_RUN,
    )


# --- the deterministic spine: arc runs in order, chain valid ------------------


def test_loop_runs_full_arc_in_order(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    result = run_assurance_loop(_canned_deps(), ledger=ledger)

    stages = [e.payload["stage"] for e in ledger.all() if e.action == LOOP_ACTION]
    assert tuple(LoopStage(s) for s in stages) == ARC
    assert result.exploit_before is True
    assert result.exploit_after is False
    assert result.before_fails == 10
    assert result.after_fails == 0
    assert result.remediated is True
    assert result.arc_complete is True
    assert ledger.verify_chain() is True


def test_each_stage_entry_carries_its_evidence(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    run_assurance_loop(_canned_deps(), ledger=ledger)
    by_stage = {
        e.payload["stage"]: e.payload for e in ledger.all() if e.action == LOOP_ACTION
    }
    assert by_stage["exposed"]["recipient"] == "ATTACKER-999"
    assert by_stage["mapped"]["eu_obligation_id"] == "OBL-EUAI-015"
    assert by_stage["mapped"]["india_obligation_id"] == "OBL-RBI-001"
    assert by_stage["verified"]["before_fails"] == 10
    assert by_stage["verified"]["after_fails"] == 0


# --- the milestone "assert the arc" check rejects incomplete / disordered -----


def _write_stages(ledger: Ledger, stages: list[str]) -> None:
    for stage in stages:
        ledger.append(
            agent="x", layer="L2", action=LOOP_ACTION, payload={"stage": stage}
        )


def test_arc_check_rejects_missing_stage(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    _write_stages(ledger, ["exposed", "detected", "mapped", "verified"])  # no patch
    assert assert_assurance_arc(ledger) is False


def test_arc_check_rejects_out_of_order(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "l.db")
    _write_stages(ledger, ["detected", "exposed", "mapped", "patched", "verified"])
    assert assert_assurance_arc(ledger) is False


def test_loop_raises_when_no_prompt_injection_finding(tmp_path: Path) -> None:
    deps = LoopDeps(
        expose=lambda: _EXPOSED,
        detect=lambda: [],  # Garak found nothing
        rescan=lambda: GUARDED,
        reverify=lambda: _GUARDED_RUN,
    )
    with pytest.raises(AssuranceLoopError, match="no prompt-injection finding"):
        run_assurance_loop(deps, ledger=Ledger(tmp_path / "l.db"))


# --- NAT workflow config validates without a live run -------------------------


def test_assurance_workflow_config_loads() -> None:
    text = ASSURANCE_WORKFLOW_CONFIG.read_text(encoding="utf-8")
    assert "_type: keystone_assurance_loop" in text
    config = AssuranceLoopConfig(prompt_cap=12)
    assert config.prompt_cap == 12


# --- the live milestone: full loop via NAT (slow; skips cleanly) --------------


def _ollama_up() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2.0)
    except httpx.HTTPError:
        return False
    return True


@pytest.mark.slow
@pytest.mark.milestone
def test_live_assurance_loop_via_nat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if shutil.which("garak") is None and shutil.which("uv") is None:
        pytest.skip("garak CLI not available")
    if not _ollama_up():
        pytest.skip("Ollama not running")

    db = tmp_path / "milestone.db"
    monkeypatch.setenv("KEYSTONE_LEDGER_DB", str(db))

    try:
        asyncio.run(run_milestone())
    except Exception as exc:  # noqa: BLE001  # surface any live failure as a skip-or-fail
        if "garak" in str(exc).lower():
            pytest.skip(f"garak unavailable: {exc}")
        raise

    ledger = Ledger(db)
    assert assert_assurance_arc(ledger) is True  # full ordered arc, hash-valid
    verified = next(
        e.payload
        for e in ledger.all()
        if e.payload.get("stage") == LoopStage.VERIFIED.value
    )
    print(
        f"\nLIVE loop: garak before={verified['before_fails']} "
        f"after={verified['after_fails']} remediated={verified['remediated']}"
    )
    assert verified["before_fails"] > 0  # Garak found the vuln unguarded
    assert verified["after_fails"] == 0  # guarded re-scan is clean
    assert verified["remediated"] is True
