"""Tests for the curated obligation graph (KS-0201).

Fast, deterministic, no inference and no network. Two layers:

* **Curation tests** assert the shipped data file satisfies KS-0201's
  ``done_criteria`` (25-30 nodes; all instruments incl. EU AI Act Art. 9-15;
  every node carries a non-empty, well-formed citation).
* **Fail-loud tests** assert the loader and model reject malformed data instead
  of degrading silently (ADR-0012 decisions 2 and the cross-field validators).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from keystone.core.obligations import (
    Citation,
    Instrument,
    Jurisdiction,
    Modality,
    Obligation,
    ObligationLoadError,
    load_obligations,
)
from keystone.core.obligations.loader import DATA_PATH

# EU AI Act articles KS-0201 must cover (Chapter III, Section 2).
_EU_AI_ACT_ARTICLES = set(range(9, 16))


@pytest.fixture(scope="module")
def obligations() -> list[Obligation]:
    return load_obligations()


# --- Curation / done_criteria ------------------------------------------------


def test_node_count_in_range(obligations: list[Obligation]) -> None:
    assert 25 <= len(obligations) <= 30


def test_all_instruments_present(obligations: list[Obligation]) -> None:
    present = {o.instrument for o in obligations}
    assert present == set(Instrument)


def test_eu_ai_act_covers_articles_9_to_15(obligations: list[Obligation]) -> None:
    found: set[int] = set()
    for o in obligations:
        if o.instrument is Instrument.EU_AI_ACT:
            match = re.search(r"\d+", o.citation.provision)
            assert match is not None, o.citation.provision
            found.add(int(match.group()))
    assert found >= _EU_AI_ACT_ARTICLES


def test_every_node_has_non_empty_citation(obligations: list[Obligation]) -> None:
    for o in obligations:
        assert o.citation.provision.strip()
        assert o.citation.title.strip()
        # The cross-field validator guarantees this, but assert it as the
        # behavioural contract KS-0205 will gate on.
        assert o.citation.instrument is o.instrument


def test_every_node_has_non_empty_summary(obligations: list[Obligation]) -> None:
    assert all(o.summary.strip() for o in obligations)


def test_ids_are_unique(obligations: list[Obligation]) -> None:
    ids = [o.id for o in obligations]
    assert len(ids) == len(set(ids))


def test_both_modalities_present(obligations: list[Obligation]) -> None:
    # Feeds KS-0203's hard-law vs. self-certification contrast.
    present = {o.enforcement_modality for o in obligations}
    assert present == set(Modality)


def test_both_jurisdictions_present(obligations: list[Obligation]) -> None:
    present = {o.jurisdiction for o in obligations}
    assert present == set(Jurisdiction)


def test_load_is_deterministic(obligations: list[Obligation]) -> None:
    again = load_obligations()
    assert [o.model_dump() for o in obligations] == [o.model_dump() for o in again]


def test_shipped_data_path_exists() -> None:
    assert DATA_PATH.is_file()


# --- Fail-loud loader --------------------------------------------------------


def _write(tmp_path: Path, payload: object) -> Path:
    path = tmp_path / "obligations.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_node() -> dict[str, object]:
    return {
        "id": "OBL-EUAI-009",
        "instrument": "EU_AI_ACT",
        "citation": {
            "instrument": "EU_AI_ACT",
            "provision": "Art. 9",
            "title": "Risk management system",
        },
        "summary": "A risk management system shall be maintained.",
        "enforcement_modality": "HARD_LAW",
        "jurisdiction": "EU",
    }


def test_loader_accepts_a_valid_minimal_node(tmp_path: Path) -> None:
    loaded = load_obligations(_write(tmp_path, [_valid_node()]))
    assert len(loaded) == 1
    assert loaded[0].control_ids == []


def test_loader_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ObligationLoadError, match="not found"):
        load_obligations(tmp_path / "nope.json")


def test_loader_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "obligations.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ObligationLoadError, match="not valid JSON"):
        load_obligations(path)


def test_loader_rejects_non_array(tmp_path: Path) -> None:
    with pytest.raises(ObligationLoadError, match="JSON array"):
        load_obligations(_write(tmp_path, {"id": "OBL-EUAI-009"}))


def test_loader_rejects_duplicate_id(tmp_path: Path) -> None:
    with pytest.raises(ObligationLoadError, match="duplicate"):
        load_obligations(_write(tmp_path, [_valid_node(), _valid_node()]))


def test_loader_rejects_unknown_enum(tmp_path: Path) -> None:
    node = _valid_node()
    node["instrument"] = "NOT_A_REAL_INSTRUMENT"
    node["citation"] = {**node["citation"], "instrument": "NOT_A_REAL_INSTRUMENT"}  # type: ignore[dict-item]
    with pytest.raises(ObligationLoadError, match="index 0 is invalid"):
        load_obligations(_write(tmp_path, [node]))


def test_loader_rejects_missing_citation_field(tmp_path: Path) -> None:
    node = _valid_node()
    del node["citation"]
    with pytest.raises(ObligationLoadError, match="index 0 is invalid"):
        load_obligations(_write(tmp_path, [node]))


def test_loader_rejects_extra_field(tmp_path: Path) -> None:
    node = _valid_node()
    node["unexpected"] = "x"
    with pytest.raises(ObligationLoadError, match="index 0 is invalid"):
        load_obligations(_write(tmp_path, [node]))


# --- Model invariants --------------------------------------------------------


def _citation(instrument: Instrument = Instrument.EU_AI_ACT) -> Citation:
    return Citation(instrument=instrument, provision="Art. 9", title="Risk management")


def test_citation_instrument_must_match_obligation() -> None:
    with pytest.raises(ValueError, match="must equal"):
        Obligation(
            id="OBL-EUAI-009",
            instrument=Instrument.EU_AI_ACT,
            citation=_citation(Instrument.DORA),
            summary="x",
            enforcement_modality=Modality.HARD_LAW,
            jurisdiction=Jurisdiction.EU,
        )


def test_id_prefix_must_match_instrument() -> None:
    with pytest.raises(ValueError, match="prefix must be"):
        Obligation(
            id="OBL-DORA-009",
            instrument=Instrument.EU_AI_ACT,
            citation=_citation(),
            summary="x",
            enforcement_modality=Modality.HARD_LAW,
            jurisdiction=Jurisdiction.EU,
        )


def test_id_must_match_pattern() -> None:
    with pytest.raises(ValueError, match="must match"):
        Obligation(
            id="EUAI-9",
            instrument=Instrument.EU_AI_ACT,
            citation=_citation(),
            summary="x",
            enforcement_modality=Modality.HARD_LAW,
            jurisdiction=Jurisdiction.EU,
        )


def test_empty_summary_rejected() -> None:
    with pytest.raises(ValueError, match="summary must be non-empty"):
        Obligation(
            id="OBL-EUAI-009",
            instrument=Instrument.EU_AI_ACT,
            citation=_citation(),
            summary="   ",
            enforcement_modality=Modality.HARD_LAW,
            jurisdiction=Jurisdiction.EU,
        )


def test_empty_citation_provision_rejected() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        Citation(instrument=Instrument.EU_AI_ACT, provision="  ", title="t")
