"""Build / save / load the run-result — the demo's typed contract for the UI.

`build_run_result` runs the KS-0405 Layer-1 milestone arc once (the authoritative
arc + hash-chained ledger) and assembles a `RunResult` from real artifacts: it
re-derives the seam transaction and the FATF finding deterministically from the
SAME seeded stream the arc used, asserts the binding is consistent (same tx id),
and reads the narrative / report / sign-off straight from the ledger it just
wrote. Composition only — no new detection capability.

Offline by default: with no `narrate` given it uses the deterministic template
narrative (no Ollama, no network), so `python -m keystone.demo` produces a saved
run without a live backend. Pass `narrate=live_narrate` for the LLM edge.

`save_run_result` / `load_run_result` round-trip the result through JSON so a saved
run replays identically (KS-0504 fallback).
"""

from __future__ import annotations

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from keystone.assurance import FAMILY_MAPPINGS, MEMO_INJECTION_SIGNATURE
from keystone.assurance.layer1_milestone import (
    DEFAULT_SIGNER,
    MILESTONE_ACTION,
    Narrator,
    run_layer1_milestone,
)
from keystone.assurance.seam import seam_fraud_stream
from keystone.core.fatf import Typology, detect
from keystone.core.ledger import Ledger
from keystone.core.reporting import ReportFacts, assemble_facts, template_narrative
from keystone.llm.report_narrative import GuardedNarrative

from .run_result import (
    RUN_RESULT_SCHEMA_VERSION,
    AiSecurityView,
    ArcView,
    FinancialCrimeView,
    RegulatoryMappingView,
    ReportView,
    RunResult,
    SeamBindingView,
    SeamTransactionView,
)

# The probe family whose curated OWASP/regulatory mapping describes the seam's
# Layer-2 vulnerability (memo prompt-injection) — see keystone.assurance.garak_probe.
_INJECTION_FAMILY = "promptinject"

# Default on-disk location for a saved run (replay / offline fallback).
DEFAULT_RUN_PATH = "keystone-run.json"


class RunResultError(Exception):
    """Raised when the arc does not yield a consistent, bindable run-result."""


def run_json_path() -> str:
    """Path to the saved run-result, from `KEYSTONE_RUN_JSON` or the default."""
    return os.environ.get("KEYSTONE_RUN_JSON", DEFAULT_RUN_PATH)


def _template_narrate(facts: ReportFacts) -> GuardedNarrative:
    """The offline default: the deterministic, always-faithful template narrative."""
    return GuardedNarrative(text=template_narrative(facts), fell_back=False)


def _assemble(ledger: Ledger, narrate: Narrator, signer: str) -> RunResult:
    """Run the arc on `ledger` and assemble the typed run-result from it."""
    res = run_layer1_milestone(narrate=narrate, signer=signer, ledger=ledger)

    # Re-derive the typed artifacts deterministically from the same seeded stream
    # the arc used; the binding is only honest if it lands on the same transaction.
    stream, seam_tx_id = seam_fraud_stream()
    if seam_tx_id != res.seam_transaction_id:
        raise RunResultError(
            f"seam transaction mismatch: arc {res.seam_transaction_id} "
            f"vs re-derived {seam_tx_id}"
        )
    seam_txn = next(t for t in stream if t.id == seam_tx_id)
    finding = next(
        (
            f
            for f in detect(stream)
            if f.typology is Typology.STRUCTURING and seam_tx_id in f.transaction_ids
        ),
        None,
    )
    if finding is None:
        raise RunResultError(f"FATF engine did not flag seam transaction {seam_tx_id}")
    facts = assemble_facts(finding, stream)

    entries = ledger.all()
    by_stage = {
        e.payload["stage"]: e.payload for e in entries if e.action == MILESTONE_ACTION
    }
    reported, signed, seam = (
        by_stage["reported"],
        by_stage["signed"],
        by_stage["seam_bound"],
    )

    sig = MEMO_INJECTION_SIGNATURE
    mapping = FAMILY_MAPPINGS[_INJECTION_FAMILY]

    return RunResult(
        schema_version=RUN_RESULT_SCHEMA_VERSION,
        generated_at=datetime.now(UTC).isoformat(),
        seam_transaction=SeamTransactionView(
            id=seam_txn.id,
            timestamp=seam_txn.timestamp.isoformat(),
            sender_account=seam_txn.sender_account,
            recipient_account=seam_txn.recipient_account,
            amount=seam_txn.amount,
            currency=seam_txn.currency.value,
            tx_type=seam_txn.tx_type.value,
            memo=seam_txn.memo,
        ),
        financial_crime=FinancialCrimeView(
            layer="L1",
            typology=finding.typology.value,
            severity=finding.severity.value,
            account=finding.account,
            transaction_ids=finding.transaction_ids,
            signal=dict(finding.signal),
            rationale=finding.rationale,
        ),
        ai_security=AiSecurityView(
            layer="L2",
            signature_name=sig.name,
            field=sig.field.value,
            mechanism=sig.mechanism.value,
            outcome=sig.outcome.value,
            exploit_tool=sig.exploit_tool,
            description=sig.description,
            l2_reference=str(seam["l2_reference"]),
            regulatory=RegulatoryMappingView(**mapping.model_dump()),
        ),
        binding=SeamBindingView(
            transaction_id=seam_tx_id,
            signature_name=sig.name,
            fatf_typology=finding.typology.value,
            thesis=str(seam["thesis"]),
        ),
        report=ReportView(
            report_format=str(reported["report_format"]),
            status=str(signed["status"]),
            signed_by=str(signed["signed_by"]),
            narrative=str(reported["narrative"]),
            narrative_fell_back=bool(reported["narrative_fell_back"]),
            currency=facts.currency,
            total_amount=float(reported["total_amount"]),
            transaction_count=int(reported["transaction_count"]),
            period_start=facts.period_start.isoformat(),
            period_end=facts.period_end.isoformat(),
        ),
        arc=ArcView(
            stages=tuple(
                str(e.payload["stage"]) for e in entries if e.action == MILESTONE_ACTION
            ),
            arc_complete=res.arc_complete,
            chain_verified=ledger.verify_chain(),
            entries=tuple(entries),
        ),
    )


def build_run_result(
    *,
    narrate: Narrator | None = None,
    signer: str = DEFAULT_SIGNER,
    ledger: Ledger | None = None,
) -> RunResult:
    """Run one Layer-1 arc and return it as a typed `RunResult`.

    With no `ledger`, runs on a throwaway ledger so the run-result is one clean
    arc (the shared persistent ledger would accumulate stages across runs and break
    the exact-arc check). With no `narrate`, uses the offline template narrative.
    """
    narr = narrate if narrate is not None else _template_narrate
    if ledger is not None:
        return _assemble(ledger, narr, signer)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        return _assemble(Ledger(Path(tmp) / "run.db"), narr, signer)


def save_run_result(result: RunResult, path: str | Path | None = None) -> Path:
    """Write the run-result to disk as indented JSON. Returns the path written."""
    out = Path(path) if path is not None else Path(run_json_path())
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return out


def load_run_result(path: str | Path | None = None) -> RunResult:
    """Load a saved run-result for replay (KS-0504 offline fallback)."""
    src = Path(path) if path is not None else Path(run_json_path())
    return RunResult.model_validate_json(src.read_text(encoding="utf-8"))
