"""Tests for the Garak red-team probe pipeline (KS-0303).

The FAST gate runs entirely over CAPTURED Garak v0.15.1 JSONL fixtures (real
output from live runs, committed under tests/fixtures/garak) — NO Garak run, NO
Ollama, NO network. That is where the coverage lives: parsing, the OWASP/
regulation mapping, the "did Garak find OUR vulnerability?" check, and the ledger
write. The single live scan is `-m slow` and skips cleanly when garak/Ollama are
unavailable (it is also how the fixtures are refreshed).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import httpx
import pytest

from keystone.assurance import (
    PINNED_GARAK_VERSION,
    GarakError,
    GarakFinding,
    GarakMappingError,
    found_our_vulnerability,
    map_finding,
    parse_report,
    record_finding,
    scan_mock_agent,
)
from keystone.assurance.garak_probe import (
    LEDGER_ACTION,
    LEDGER_AGENT,
    _report_path_from_output,
)
from keystone.core.ledger import Ledger

_FIXTURES = Path(__file__).parent / "fixtures" / "garak"
VULNERABLE_REPORT = _FIXTURES / "latentinjection_vulnerable.report.jsonl"
CLEAN_REPORT = _FIXTURES / "latentinjection_clean.report.jsonl"


# --- parser -------------------------------------------------------------------


def test_parse_vulnerable_report_extracts_the_finding() -> None:
    findings = parse_report(VULNERABLE_REPORT)
    assert len(findings) == 1
    finding = findings[0]
    assert finding.probe == "latentinjection.LatentInjectionTranslationEnFr"
    assert finding.family == "latentinjection"
    assert finding.fails == 10
    assert finding.total_evaluated == 12
    assert finding.is_hit is True
    assert finding.failure_rate == pytest.approx(10 / 12)


def test_parse_clean_report_has_no_hit() -> None:
    findings = parse_report(CLEAN_REPORT)
    assert len(findings) == 1
    assert findings[0].fails == 0
    assert findings[0].is_hit is False


def test_failure_rate_guards_zero_total() -> None:
    empty = GarakFinding(
        probe="latentinjection.X",
        detector="d",
        passed=0,
        fails=0,
        nones=0,
        total_evaluated=0,
    )
    assert empty.failure_rate == 0.0
    assert empty.is_hit is False


def test_parse_missing_report_raises() -> None:
    with pytest.raises(GarakError, match="cannot read"):
        parse_report(_FIXTURES / "does-not-exist.report.jsonl")


def test_parse_malformed_jsonl_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.report.jsonl"
    bad.write_text('{"entry_type": "eval"\n', encoding="utf-8")  # truncated JSON
    with pytest.raises(GarakError, match="malformed JSONL"):
        parse_report(bad)


# --- mapping (OWASP + EU Art.15 + India principle) ----------------------------


def test_prompt_injection_maps_to_owasp_and_regulation() -> None:
    finding = parse_report(VULNERABLE_REPORT)[0]
    mapped = map_finding(finding)
    m = mapped.mapping
    assert "LLM01" in m.owasp_llm
    assert "ASI" in m.owasp_agentic or "Agentic" in m.owasp_agentic
    assert "Art. 15" in m.eu_ai_act
    assert m.eu_obligation_id == "OBL-EUAI-015"  # curated, validated citation
    assert m.india_obligation_id == "OBL-RBI-001"


def test_unknown_probe_family_has_no_mapping() -> None:
    rogue = GarakFinding(
        probe="malwaregen.Evasion",
        detector="x",
        passed=0,
        fails=1,
        nones=0,
        total_evaluated=1,
    )
    with pytest.raises(GarakMappingError, match="no OWASP/regulation mapping"):
        map_finding(rogue)


# --- the "found our vulnerability?" check -------------------------------------


def test_found_our_vulnerability_true_on_vulnerable_fixture() -> None:
    assert found_our_vulnerability(parse_report(VULNERABLE_REPORT)) is True


def test_found_our_vulnerability_false_on_clean_fixture() -> None:
    assert found_our_vulnerability(parse_report(CLEAN_REPORT)) is False


# --- ledger finding entry -----------------------------------------------------


def test_record_finding_writes_mapped_entry(tmp_path: Path) -> None:
    ledger = Ledger(tmp_path / "ledger.db")
    finding = parse_report(VULNERABLE_REPORT)[0]
    entry = record_finding(map_finding(finding), ledger=ledger)

    assert entry.agent == LEDGER_AGENT
    assert entry.layer == "L2"
    assert entry.action == LEDGER_ACTION
    payload = entry.payload
    assert payload["probe"] == "latentinjection.LatentInjectionTranslationEnFr"
    assert payload["fails"] == 10
    assert payload["owasp_llm"].startswith("LLM01")
    assert payload["eu_obligation_id"] == "OBL-EUAI-015"
    assert payload["india_obligation_id"] == "OBL-RBI-001"
    assert payload["garak_version"] == PINNED_GARAK_VERSION
    assert payload["vulnerability_signature"] == "memo-instruction-injection"
    assert ledger.verify_chain() is True


# --- pinned version + stdout parsing (pure helpers) ---------------------------


def test_pinned_garak_version() -> None:
    assert PINNED_GARAK_VERSION == "0.15.1"


def test_report_path_extracted_from_garak_stdout() -> None:
    stdout = "🦜 loading generator\n📜 reporting to C:/x/run.report.jsonl\n✔️ done\n"
    assert _report_path_from_output(stdout) == Path("C:/x/run.report.jsonl")


def test_report_path_none_when_absent() -> None:
    assert _report_path_from_output("no report line here") is None


# --- live scan (slow; skips cleanly if garak/Ollama unavailable) --------------


def _ollama_up() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=2.0)
    except httpx.HTTPError:
        return False
    return True


@pytest.mark.slow
def test_live_garak_finds_memo_injection_vuln(tmp_path: Path) -> None:
    if shutil.which("garak") is None and shutil.which("uv") is None:
        pytest.skip("garak CLI not available")
    if not _ollama_up():
        pytest.skip("Ollama not running")

    try:
        report = scan_mock_agent(report_prefix="ks0303_test_live", prompt_cap=8)
    except GarakError as exc:
        pytest.skip(f"garak unavailable: {exc}")

    findings = parse_report(report)
    print(
        f"\nLIVE garak findings: {[(f.probe, f.fails, f.total_evaluated) for f in findings]}"
    )
    assert found_our_vulnerability(findings) is True
