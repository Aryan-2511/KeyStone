"""The demo run-result (KS-0500) — the UI's typed contract over the Layer-1 arc.

These assert the run-result is a faithful VIEW of a real arc (no placeholder data):
it carries the real seam transaction, both findings, and the canonical signature;
the two findings bind to the SAME transaction id; the arc is whole, ordered and
hash-valid; and the result round-trips through JSON so a saved run replays
identically (the KS-0504 offline-fallback path).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from keystone.assurance import (
    FAMILY_MAPPINGS,
    MEMO_INJECTION_SIGNATURE,
    REFERENCED_ASSURANCE,
)
from keystone.assurance.layer1_milestone import ARC
from keystone.assurance.signature import CANONICAL_MEMO_EXPLOIT
from keystone.core.ledger import Ledger
from keystone.demo import (
    RUN_RESULT_SCHEMA_VERSION,
    RunResult,
    RunResultError,
    build_run_result,
    load_run_result,
    save_run_result,
)
from keystone.demo import __main__ as cli


def _run(tmp_path: Path) -> RunResult:
    """Build a run-result on an isolated, fresh ledger (offline template narrative)."""
    return build_run_result(ledger=Ledger(tmp_path / "run.db"))


# --- the binding: ONE transaction, both findings, the canonical signature -----


def test_both_findings_bind_to_the_same_seam_transaction(tmp_path: Path) -> None:
    rr = _run(tmp_path)
    seam_id = rr.binding.transaction_id

    # The Layer-1 financial-crime finding implicates the seam transaction...
    assert seam_id in rr.financial_crime.transaction_ids
    assert rr.financial_crime.typology == rr.binding.fatf_typology
    # ...and the Layer-2 vulnerability and the binding name the SAME canonical signature.
    assert rr.binding.signature_name == MEMO_INJECTION_SIGNATURE.name
    assert rr.ai_security.signature_name == MEMO_INJECTION_SIGNATURE.name
    # The seam transaction view is the same object both sides reference.
    assert rr.seam_transaction.id == seam_id


def test_values_come_from_the_real_run_not_hardcoded(tmp_path: Path) -> None:
    rr = _run(tmp_path)

    # The seam transaction carries the real canonical exploit memo (the L2 locus).
    assert rr.seam_transaction.memo == CANONICAL_MEMO_EXPLOIT.memo
    assert rr.seam_transaction.amount > 0

    # The L2 view is the canonical signature, verbatim.
    sig = MEMO_INJECTION_SIGNATURE
    assert (rr.ai_security.field, rr.ai_security.mechanism, rr.ai_security.outcome) == (
        sig.field.value,
        sig.mechanism.value,
        sig.outcome.value,
    )
    assert rr.ai_security.description == sig.description

    # The regulatory mapping is the curated assurance mapping, verbatim (feeds KS-0502).
    mapping = FAMILY_MAPPINGS["promptinject"]
    assert rr.ai_security.regulatory.owasp_llm == mapping.owasp_llm
    assert rr.ai_security.regulatory.eu_obligation_id == mapping.eu_obligation_id
    assert rr.ai_security.regulatory.india_obligation_id == mapping.india_obligation_id


def test_regulatory_modality_is_read_from_the_obligation_graph(tmp_path: Path) -> None:
    # The EU/India enforcement modalities come from the real obligation graph (the
    # KS-0502 hard-law vs self-certification contrast), not assumed by jurisdiction.
    reg = _run(tmp_path).ai_security.regulatory
    assert reg.eu_modality == "HARD_LAW"
    assert reg.india_modality == "SELF_CERTIFICATION"


def test_report_renders_both_regulator_formats_from_one_fact_model(
    tmp_path: Path,
) -> None:
    # The SAME facts rendered into FINnet (India) AND goAML (UN) — the pluggable-
    # connector claim. Same transactions, same total, two shapes.
    report = _run(tmp_path).report
    finnet, goaml = report.finnet, report.goaml

    assert finnet["report_type"] == "STR" and goaml["report_code"] == "STR"
    assert finnet["total_amount"] == report.total_amount

    finnet_txns = finnet["suspicious_transactions"]
    goaml_txns = goaml["transactions"]
    assert isinstance(finnet_txns, list) and isinstance(goaml_txns, list)
    assert len(finnet_txns) == len(goaml_txns)
    # Different field NAMES for the same fact (the "different shape" point).
    assert isinstance(finnet_txns[0], dict) and isinstance(goaml_txns[0], dict)
    assert "transaction_id" in finnet_txns[0]
    assert "transactionnumber" in goaml_txns[0]


def test_assurance_before_after_is_the_referenced_canonical_result(
    tmp_path: Path,
) -> None:
    # The L2 before/after (KS-0304) is REFERENCED, not re-run: it equals the canonical
    # constant and reads as a real "found N, fixed to 0" remediation.
    a = _run(tmp_path).ai_security.assurance
    assert a.before_fails == REFERENCED_ASSURANCE.before_fails > 0
    assert a.after_fails == 0
    assert a.exploit_before is True and a.exploit_after is False
    assert a.remediated is True
    assert a.prompt_cap == REFERENCED_ASSURANCE.prompt_cap


def test_arc_is_whole_ordered_and_chain_valid(tmp_path: Path) -> None:
    rr = _run(tmp_path)

    assert rr.arc.stages == tuple(stage.value for stage in ARC)
    assert rr.arc.arc_complete is True
    assert rr.arc.chain_verified is True
    assert rr.arc.entry_count == len(ARC)


def test_report_is_drafted_signed_and_faithful(tmp_path: Path) -> None:
    rr = _run(tmp_path)

    assert rr.report.report_format == "FINNET"
    assert rr.report.status == "SIGNED"
    assert rr.report.signed_by
    assert rr.report.narrative  # non-empty
    # The offline default uses the deterministic, faithful template (no fall-back).
    assert rr.report.narrative_fell_back is False
    assert rr.report.total_amount > 0


# --- replay: the run-result round-trips through JSON --------------------------


def test_run_result_round_trips_through_json(tmp_path: Path) -> None:
    rr = _run(tmp_path)
    out = save_run_result(rr, tmp_path / "saved.json")
    assert out.is_file()

    loaded = load_run_result(out)
    assert loaded == rr
    assert loaded.schema_version == RUN_RESULT_SCHEMA_VERSION
    # The loaded run re-verifies its own hash chain (offline evidence is intact).
    assert loaded.arc.chain_verified is True


def test_loading_a_mismatched_schema_run_raises_a_clear_error(tmp_path: Path) -> None:
    # A saved run from a different schema_version (e.g. a v1 run after the v2
    # migration) must fail with a clear, actionable RunResultError — never a cryptic
    # pydantic "extra inputs"/"field required" wall that crashes the replay screen.
    rr = _run(tmp_path)
    data = json.loads(
        save_run_result(rr, tmp_path / "r.json").read_text(encoding="utf-8")
    )
    data["schema_version"] = RUN_RESULT_SCHEMA_VERSION - 1  # pretend it's the old shape
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(RunResultError) as exc:
        load_run_result(stale)
    assert "schema" in str(exc.value).lower()
    # It is a ValueError, so the UI's replay except-clause degrades gracefully.
    assert isinstance(exc.value, ValueError)


def test_build_on_default_ledger_produces_a_clean_arc() -> None:
    # No ledger passed: the runner uses a throwaway ledger so one call is one clean,
    # complete arc (the shared persistent ledger would accumulate stages).
    rr = build_run_result()
    assert rr.arc.arc_complete is True
    assert rr.arc.stages == tuple(stage.value for stage in ARC)


def test_cli_writes_a_loadable_run(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "cli-run.json"
    cli.main_with_args([str(out)])

    loaded = load_run_result(out)
    assert loaded.arc.chain_verified is True
    captured = capsys.readouterr().out
    assert str(out) in captured
    assert loaded.binding.transaction_id in captured
