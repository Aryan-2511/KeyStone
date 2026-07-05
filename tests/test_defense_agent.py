"""The Defense Agent (MC-01) — the honesty tests (MC-00 §3).

Keystone's third genuine agent chooses which remediation a finding warrants — (a) block the
AI-side injection vs (c) tighten the money-side detection — via a transparent, finding-dependent
policy (NOT an LLM). These tests pin the guarantees the design fixed BEFORE code:

1. **The flip** — a strong-AI/weak-financial finding chooses (a); a weak-AI/strong-financial
   finding chooses (c). If the choice never flips it is a fixed dispatch (theater) — fail.
2. **All-options-reachable** — both (a) and (c) are genuinely chosen by some real finding.
3. **Same-finding determinism** — the policy is a pure function of the finding.
4. **Memo-blind (sacred)** — the agent reads signals only; the choice never touches the memo.
5. **Uniform interface** — both remediations implement apply()->RemediationOutcome; the agent
   dispatches uniformly, keeping the seam-side difference.

Deterministic, fast-gated — no LLM, no network, no Garak.
"""

from __future__ import annotations

import datetime

from keystone.agents.defense import (
    DEFENSE_FLOOR,
    DefenseSignals,
    choose_remediation,
    defend,
)
from keystone.agents.triage import FindingSeverity, SeamClassification
from keystone.assurance.remediation import (
    FINANCIAL_TIGHTENING_CONTROL,
    GUARDRAIL_PATCH_CONTROL,
    RemediationContext,
    SeamSide,
)
from keystone.core.transactions import Currency, Transaction, TransactionType


def _signals(
    failure_rate: float,
    financial_gap: bool,
    *,
    seam_result: SeamClassification = SeamClassification.CLEAN,
    severity: FindingSeverity = FindingSeverity.HIGH,
) -> DefenseSignals:
    return DefenseSignals(
        failure_rate=failure_rate,
        financial_gap=financial_gap,
        seam_result=seam_result,
        severity=severity,
    )


# The two discriminating findings (MC-00 §0 — genuine, from real primitives):
#   (a)-favoring: injection landed hard, the money is already detected (no gap).
#   (c)-favoring: injection contained, a transaction slips detection (a gap tightening catches).
_A_FAVORING = _signals(0.90, financial_gap=False)  # strong-AI / weak-financial
_C_FAVORING = _signals(0.03, financial_gap=True)  # weak-AI / strong-financial


# --- 1. THE FLIP (the proof it is an agent, not a dispatch) --------------------


def test_the_choice_flips_between_a_favoring_and_c_favoring_findings() -> None:
    a = defend(_A_FAVORING)
    c = defend(_C_FAVORING)
    assert a.remediation.control == GUARDRAIL_PATCH_CONTROL  # (a) AI-side
    assert a.remediation.side is SeamSide.AI
    assert c.remediation.control == FINANCIAL_TIGHTENING_CONTROL  # (c) financial-side
    assert c.remediation.side is SeamSide.FINANCIAL
    assert (
        a.remediation.control != c.remediation.control
    )  # the choice genuinely flipped


def test_both_signals_matter_not_a_single_threshold() -> None:
    # (c) needs BOTH a financial gap AND a contained injection — flip either and it becomes (a).
    assert choose_remediation(_signals(0.03, True)).side is SeamSide.FINANCIAL
    assert (
        choose_remediation(_signals(0.03, False)).side is SeamSide.AI
    )  # no gap -> (a)
    assert (
        choose_remediation(_signals(0.90, True)).side is SeamSide.AI
    )  # injection live -> (a)


# --- 2. ALL OPTIONS REACHABLE (neither remediation is dead) -------------------


def test_all_remediations_are_reachable() -> None:
    chosen = {
        defend(_A_FAVORING).remediation.control,
        defend(_C_FAVORING).remediation.control,
    }
    assert chosen == {GUARDRAIL_PATCH_CONTROL, FINANCIAL_TIGHTENING_CONTROL}


# --- 3. SAME-FINDING DETERMINISM ----------------------------------------------


def test_same_finding_same_remediation() -> None:
    first = defend(_C_FAVORING)
    second = defend(_C_FAVORING)
    assert first.remediation.control == second.remediation.control
    assert first.rationale == second.rationale
    assert first.reasoner == "policy"  # policy-first, never an LLM (MC-01)


# --- 4. THE UNIFORM INTERFACE (apply()->RemediationOutcome, side preserved) ---


def test_c_apply_re_runs_memo_blind_detection_and_reports_the_gap() -> None:
    # A lone 9,000 transfer the baseline misses; (c)'s apply, over the run context, reports it
    # as newly covered — verified_offline True (an offline detection change).
    lone = Transaction(
        id="TXN-009001",
        timestamp=datetime.datetime(2026, 3, 1, tzinfo=datetime.UTC),
        sender_account="ACC-9001",
        recipient_account="ACC-0042",
        amount=9_000.0,
        currency=Currency.USD,
        tx_type=TransactionType.TRANSFER,
    )
    decision = defend(
        _C_FAVORING, context=RemediationContext(stream=(lone,), operative_tx_id=lone.id)
    )
    out = decision.outcome
    assert out.side is SeamSide.FINANCIAL
    assert out.verified_offline is True  # (c) is verifiable now
    assert lone.id in out.detail
    assert out.retest_via == "detect_strict"  # loop-ready handle for MC-02


def test_a_apply_records_the_control_and_defers_verification_to_the_loop() -> None:
    # (a)'s effect on this finding needs an MC-02 re-scan, so verified_offline is None (honest);
    # the re-test handle points at the guarded-agent scan.
    decision = defend(
        _A_FAVORING, context=RemediationContext(operative_tx_id="TXN-000016")
    )
    out = decision.outcome
    assert out.side is SeamSide.AI
    assert out.verified_offline is None  # not claimed offline; MC-02 verifies
    assert out.retest_via == "scan_guarded_agent"
    assert out.control == GUARDRAIL_PATCH_CONTROL


# --- 5. MEMO-BLIND: the choice depends on signals ONLY ------------------------


def test_choice_is_memo_blind_signals_only() -> None:
    # DefenseSignals carries no attack channel; the choice is a pure function of the signals.
    # (Structural: the model has only failure_rate / financial_gap / seam_result / severity.)
    fields = set(DefenseSignals.model_fields)
    assert fields == {"failure_rate", "financial_gap", "seam_result", "severity"}
    assert "memo" not in fields and "attack" not in fields


def test_floor_boundary_behaviour() -> None:
    # At exactly the floor the injection counts as live -> (a); just below, a gap -> (c).
    assert choose_remediation(_signals(DEFENSE_FLOOR, True)).side is SeamSide.AI
    assert (
        choose_remediation(_signals(DEFENSE_FLOOR - 0.001, True)).side
        is SeamSide.FINANCIAL
    )
