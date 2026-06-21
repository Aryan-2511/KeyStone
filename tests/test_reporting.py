"""Tests for regulator report generation (KS-0404).

The FAST gate is deterministic — no LLM, no network. It proves: facts are assembled
exactly from the finding + transactions; the FINnet and goAML adapters render the
SAME facts; the faithfulness guard keeps a faithful narrative but FALLS BACK to the
deterministic template when the (fake) backend invents/alters a fact; the template
is always faithful (the safe floor); sign-off transitions and ledger entries are
shaped right; and nothing mutates the source data. The single live narrative is
`-m slow` and must always be faithful (or fall back) — never an unfaithful filing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from keystone.core.fatf import Typology, detect
from keystone.core.ledger import Ledger
from keystone.core.obligations.loader import DATA_PATH as OBLIGATIONS_DATA
from keystone.core.reporting import (
    Report,
    ReportAssemblyError,
    ReportFormat,
    ReportStatus,
    assemble_facts,
    narrative_is_faithful,
    record_report,
    render,
    sign_off,
    template_narrative,
    to_finnet,
    to_goaml,
)
from keystone.core.transactions import sample_stream
from keystone.llm.inference import BackendUnreachableError
from keystone.llm.report_narrative import draft_report, generate_narrative


class _FakeBackend:
    def __init__(self, reply: str) -> None:
        self.reply = reply

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        return self.reply


# --- facts assembled exactly from finding + transactions ----------------------


def test_facts_assembled_from_finding_and_transactions() -> None:
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts = assemble_facts(finding, stream)

    implicated = [t for t in stream if t.id in finding.transaction_ids]
    assert facts.typology == "STRUCTURING"
    assert facts.account == finding.account
    assert facts.transaction_ids == tuple(finding.transaction_ids)
    assert facts.transaction_count == len(implicated)
    assert facts.amounts == tuple(t.amount for t in implicated)
    assert facts.total_amount == round(sum(t.amount for t in implicated), 2)
    assert facts.currency == "USD"
    assert facts.period_start == min(t.timestamp for t in implicated)


def test_assemble_facts_fails_loud_on_unknown_finding() -> None:
    finding = next(
        f for f in detect(sample_stream()) if f.typology is Typology.STRUCTURING
    )
    with pytest.raises(ReportAssemblyError, match="no known transactions"):
        assemble_facts(finding, [])  # no transactions to resolve the ids


# --- format adapters: same facts, two formats ---------------------------------


def test_finnet_and_goaml_render_the_same_facts() -> None:
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts = assemble_facts(finding, stream)
    report = Report(
        facts=facts, narrative=template_narrative(facts), narrative_fell_back=False
    )

    finnet = to_finnet(report)
    goaml = to_goaml(report)

    assert finnet["report_type"] == "STR"
    assert finnet["ground_of_suspicion"] == "STRUCTURING"
    assert len(finnet["suspicious_transactions"]) == facts.transaction_count
    assert finnet["reporting_entity"]["re_id"] == "<PLACEHOLDER>"  # marked placeholder

    assert goaml["report_code"] == "STR"
    assert goaml["report_indicator"] == "STRUCTURING"
    assert len(goaml["transactions"]) == facts.transaction_count

    # Format-agnostic core: the SAME implicated tx ids and total in both formats.
    finnet_ids = [t["transaction_id"] for t in finnet["suspicious_transactions"]]
    goaml_ids = [t["transactionnumber"] for t in goaml["transactions"]]
    assert finnet_ids == goaml_ids == list(facts.transaction_ids)
    assert finnet["total_amount"] == facts.total_amount
    assert render(report, ReportFormat.GOAML) == goaml


# --- the faithfulness guard (fake backend) ------------------------------------


def test_template_narrative_is_always_faithful() -> None:
    facts = assemble_facts(
        next(f for f in detect(sample_stream()) if f.typology is Typology.STRUCTURING),
        sample_stream(),
    )
    assert narrative_is_faithful(template_narrative(facts), facts) is True


def test_faithful_narrative_is_kept() -> None:
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts = assemble_facts(finding, stream)
    backend = _FakeBackend(template_narrative(facts))  # faithful by construction

    result = generate_narrative(facts, backend=backend)
    assert result.fell_back is False
    assert result.text == template_narrative(facts)


@pytest.mark.parametrize(
    "lie",
    [
        "Account ACC-0004 transferred 999999.00 USD in total.",  # invented amount
        "Transaction TXN-999999 was suspicious.",  # invented id
        "A LARGE_TRANSFER pattern was found on ACC-0004.",  # wrong typology
    ],
)
def test_unfaithful_narrative_falls_back_to_template(lie: str) -> None:
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts = assemble_facts(finding, stream)

    result = generate_narrative(facts, backend=_FakeBackend(lie))
    assert result.fell_back is True
    assert result.text == template_narrative(facts)  # the safe floor
    assert narrative_is_faithful(result.text, facts) is True


def test_empty_narrative_falls_back() -> None:
    facts = assemble_facts(
        next(f for f in detect(sample_stream()) if f.typology is Typology.STRUCTURING),
        sample_stream(),
    )
    result = generate_narrative(facts, backend=_FakeBackend("   "))
    assert result.fell_back is True


def test_faithful_narrative_may_cite_real_ids_without_falling_back() -> None:
    # Guard against OVER-fallback: a narrative that legitimately cites a real
    # transaction id (whose digits are not an invented amount) stays faithful.
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts = assemble_facts(finding, stream)
    cited = (
        f"Account {facts.account} ran {facts.transaction_count} structuring "
        f"transfers (e.g. {facts.transaction_ids[0]}) totalling "
        f"{facts.total_amount} {facts.currency}."
    )
    assert narrative_is_faithful(cited, facts) is True
    assert generate_narrative(facts, backend=_FakeBackend(cited)).fell_back is False


# --- human checkpoint: draft -> signed + ledger -------------------------------


def test_sign_off_transition_and_ledger(tmp_path: Path) -> None:
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    report = draft_report(finding, stream, backend=_FakeBackend("bad 999999.00"))
    assert report.status is ReportStatus.DRAFT
    assert report.narrative_fell_back is True  # the lie fell back

    ledger = Ledger(tmp_path / "l.db")
    draft_entry = record_report(report, ReportFormat.FINNET, ledger=ledger)
    assert draft_entry.action == "report_drafted"

    signed = sign_off(report, "compliance.officer@bank")
    assert signed.status is ReportStatus.SIGNED
    assert signed.signed_by == "compliance.officer@bank"
    signed_entry = record_report(signed, ReportFormat.FINNET, ledger=ledger)
    assert signed_entry.action == "report_signed"
    assert signed_entry.payload["format"] == "FINNET"
    assert signed_entry.payload["transaction_ids"] == list(report.facts.transaction_ids)
    assert signed_entry.payload["narrative_fell_back"] is True
    assert ledger.verify_chain() is True


# --- no mutation --------------------------------------------------------------


def test_generation_does_not_mutate_core_data(tmp_path: Path) -> None:
    before = OBLIGATIONS_DATA.read_bytes()
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts_before = assemble_facts(finding, stream)

    generate_narrative(facts_before, backend=_FakeBackend("totally different text"))

    assert OBLIGATIONS_DATA.read_bytes() == before  # core data byte-identical
    assert assemble_facts(finding, stream) == facts_before  # facts unchanged


# --- live narrative (slow; always faithful or falls back) ---------------------


@pytest.mark.slow
def test_live_narrative_is_never_unfaithful() -> None:
    stream = sample_stream()
    finding = next(f for f in detect(stream) if f.typology is Typology.STRUCTURING)
    facts = assemble_facts(finding, stream)
    try:
        result = generate_narrative(facts)
    except BackendUnreachableError as exc:
        pytest.skip(f"no live backend: {exc}")

    assert result.text.strip()
    # The returned narrative is ALWAYS faithful — the LLM's (if it passed) or the
    # template (on fall-back). A filing is never emitted with a hallucinated fact.
    assert narrative_is_faithful(result.text, facts) is True
    print(f"\nLIVE narrative (fell_back={result.fell_back}): {result.text[:160]}")
