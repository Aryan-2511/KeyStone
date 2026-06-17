"""Tests for the shared control library + obligations crosswalk (KS-0202).

Fast, deterministic, no inference and no network. Three layers:

* **Loader** fail-loud tests (mirror the obligation loader).
* **§5b crosswalk validator** (`scripts/validate_controls.py`): real data passes;
  a dangling reference / coverage gap / orphan control is rejected.
* **Crosswalk** lookup properties: no orphans, full coverage, modality preserved.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from validate_controls import validate as validate_crosswalk

from keystone.core.controls import (
    Control,
    ControlLoadError,
    Framework,
    SpineMapping,
    build_crosswalk,
    load_controls,
)
from keystone.core.controls.loader import DATA_PATH
from keystone.core.obligations import Modality, Obligation, load_obligations

# The control grouping is an OUTPUT of honest mapping (ADR-0012 / KS-0202), not a
# target. This snapshot pins the *stable* result so an accidental remap is caught.
_EXPECTED_GROUPING: dict[str, list[str]] = {
    "CTL-GOV-01": [
        "OBL-DORA-005",
        "OBL-DPDPA-008",
        "OBL-DPDPA-010",
        "OBL-RBI-001",
        "OBL-RBI-002",
    ],
    "CTL-RISK-01": ["OBL-DORA-006", "OBL-EUAI-009"],
    "CTL-DATA-01": ["OBL-DPDPA-008", "OBL-EUAI-010"],
    "CTL-DOC-01": ["OBL-EUAI-011", "OBL-EUAI-012"],
    "CTL-HUMAN-01": ["OBL-EUAI-014"],
    "CTL-ROBUST-01": ["OBL-DORA-024", "OBL-EUAI-015"],
    "CTL-SEC-01": ["OBL-DPDPA-008", "OBL-DPDPR-006"],
    "CTL-INC-01": ["OBL-DORA-017", "OBL-DORA-019", "OBL-DPDPA-008", "OBL-DPDPR-007"],
    "CTL-CONSENT-01": ["OBL-DPDPA-005", "OBL-DPDPA-006", "OBL-DPDPR-004"],
    "CTL-RIGHTS-01": ["OBL-DPDPA-011"],
    "CTL-TRANSP-01": ["OBL-EUAI-013", "OBL-RBI-003"],
    "CTL-CHILD-01": ["OBL-DPDPA-009"],
    "CTL-TPRM-01": ["OBL-DORA-028"],
    "CTL-CDD-01": ["OBL-PMLA-009", "OBL-PMLA-012"],
    "CTL-AMLREP-01": ["OBL-PMLA-008", "OBL-PMLA-012"],
}


@pytest.fixture(scope="module")
def controls() -> list[Control]:
    return load_controls()


# --- loader fail-loud ---------------------------------------------------------


def _write(tmp_path: Path, payload: object, name: str = "controls.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _valid_control() -> dict[str, object]:
    return {
        "id": "CTL-GOV-01",
        "title": "Governance",
        "description": "Governance and accountability.",
        "spine": [{"framework": "ISO_42001", "reference": "Clause 5 — Leadership"}],
    }


def test_load_controls_returns_library(controls: list[Control]) -> None:
    assert len(controls) >= 1
    ids = [c.id for c in controls]
    assert len(ids) == len(set(ids))  # unique


def test_every_control_has_a_spine_mapping(controls: list[Control]) -> None:
    assert all(c.spine for c in controls)


def test_shipped_controls_path_exists() -> None:
    assert DATA_PATH.is_file()


def test_loader_accepts_valid_control(tmp_path: Path) -> None:
    loaded = load_controls(_write(tmp_path, [_valid_control()]))
    assert loaded[0].id == "CTL-GOV-01"


def test_loader_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ControlLoadError, match="not found"):
        load_controls(tmp_path / "nope.json")


def test_loader_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "controls.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ControlLoadError, match="not valid JSON"):
        load_controls(path)


def test_loader_rejects_non_array(tmp_path: Path) -> None:
    with pytest.raises(ControlLoadError, match="JSON array"):
        load_controls(_write(tmp_path, {"id": "CTL-GOV-01"}))


def test_loader_rejects_duplicate_id(tmp_path: Path) -> None:
    with pytest.raises(ControlLoadError, match="duplicate"):
        load_controls(_write(tmp_path, [_valid_control(), _valid_control()]))


def test_loader_rejects_unknown_framework(tmp_path: Path) -> None:
    ctl = _valid_control()
    ctl["spine"] = [{"framework": "NOT_A_FRAMEWORK", "reference": "x"}]
    with pytest.raises(ControlLoadError, match="index 0 is invalid"):
        load_controls(_write(tmp_path, [ctl]))


def test_loader_rejects_empty_spine(tmp_path: Path) -> None:
    ctl = _valid_control()
    ctl["spine"] = []
    with pytest.raises(ControlLoadError, match="index 0 is invalid"):
        load_controls(_write(tmp_path, [ctl]))


def test_loader_rejects_missing_field(tmp_path: Path) -> None:
    ctl = _valid_control()
    del ctl["title"]
    with pytest.raises(ControlLoadError, match="index 0 is invalid"):
        load_controls(_write(tmp_path, [ctl]))


def test_loader_rejects_extra_field(tmp_path: Path) -> None:
    ctl = _valid_control()
    ctl["unexpected"] = "x"
    with pytest.raises(ControlLoadError, match="index 0 is invalid"):
        load_controls(_write(tmp_path, [ctl]))


def test_loader_rejects_bad_id_pattern(tmp_path: Path) -> None:
    ctl = _valid_control()
    ctl["id"] = "GOV-1"
    with pytest.raises(ControlLoadError, match="index 0 is invalid"):
        load_controls(_write(tmp_path, [ctl]))


def test_model_constructs_directly() -> None:
    control = Control(
        id="CTL-GOV-01",
        title="t",
        description="d",
        spine=[SpineMapping(framework=Framework.ISO_42001, reference="Clause 5")],
    )
    assert control.spine[0].framework is Framework.ISO_42001


# --- §5b crosswalk validator --------------------------------------------------


def _obligation(oid: str, control_ids: list[str]) -> dict[str, object]:
    return {
        "id": oid,
        "instrument": "EU_AI_ACT",
        "citation": {
            "instrument": "EU_AI_ACT",
            "provision": "Art. 9",
            "title": "Risk management system",
        },
        "summary": "A risk management system shall be maintained.",
        "enforcement_modality": "HARD_LAW",
        "jurisdiction": "EU",
        "control_ids": control_ids,
    }


def test_5b_real_data_passes() -> None:
    assert validate_crosswalk() == []


def test_5b_dangling_reference_rejected(tmp_path: Path) -> None:
    controls_path = _write(tmp_path, [_valid_control()])
    obligations_path = _write(
        tmp_path, [_obligation("OBL-EUAI-009", ["CTL-NONEXISTENT"])], "obligations.json"
    )
    errors = validate_crosswalk(controls_path, obligations_path)
    assert any(
        "OBL-EUAI-009" in e and "CTL-NONEXISTENT" in e and "does not resolve" in e
        for e in errors
    )


def test_5b_coverage_gap_rejected(tmp_path: Path) -> None:
    controls_path = _write(tmp_path, [_valid_control()])
    obligations_path = _write(
        tmp_path, [_obligation("OBL-EUAI-009", [])], "obligations.json"
    )
    errors = validate_crosswalk(controls_path, obligations_path)
    assert any("coverage gap" in e for e in errors)


def test_5b_orphan_control_rejected(tmp_path: Path) -> None:
    gov = _valid_control()
    risk = {**_valid_control(), "id": "CTL-RISK-01"}
    controls_path = _write(tmp_path, [gov, risk])
    obligations_path = _write(
        tmp_path, [_obligation("OBL-EUAI-009", ["CTL-GOV-01"])], "obligations.json"
    )
    errors = validate_crosswalk(controls_path, obligations_path)
    assert any("CTL-RISK-01" in e and "orphan" in e for e in errors)


# --- crosswalk lookup ---------------------------------------------------------


def test_crosswalk_has_no_orphan_controls(controls: list[Control]) -> None:
    mappings = build_crosswalk(controls, load_obligations())
    assert all(m.obligations for m in mappings)


def test_crosswalk_covers_every_obligation(controls: list[Control]) -> None:
    obligations = load_obligations()
    mappings = build_crosswalk(controls, obligations)
    mapped = {o.id for m in mappings for o in m.obligations}
    assert mapped == {o.id for o in obligations}


def test_crosswalk_preserves_both_modalities(controls: list[Control]) -> None:
    mappings = build_crosswalk(controls, load_obligations())
    both = [m for m in mappings if m.modalities == set(Modality)]
    assert both, "expected at least one control satisfied by both modalities"


def test_crosswalk_is_deterministic(controls: list[Control]) -> None:
    obligations = load_obligations()
    a = build_crosswalk(controls, obligations)
    b = build_crosswalk(controls, obligations)
    assert [(m.control.id, [o.id for o in m.obligations]) for m in a] == [
        (m.control.id, [o.id for o in m.obligations]) for m in b
    ]


def test_crosswalk_raises_on_dangling_reference(controls: list[Control]) -> None:
    bad = Obligation.model_validate(_obligation("OBL-EUAI-009", ["CTL-NONEXISTENT"]))
    with pytest.raises(ValueError, match="does not resolve"):
        build_crosswalk(controls, [bad])


# --- milestone ----------------------------------------------------------------


@pytest.mark.milestone
def test_milestone_stable_control_grouping(controls: list[Control]) -> None:
    """The crosswalk produces the curated, stable control→obligations grouping."""
    mappings = build_crosswalk(controls, load_obligations())
    grouping = {m.control.id: [o.id for o in m.obligations] for m in mappings}
    assert grouping == _EXPECTED_GROUPING
    # Modality is preserved through the lookup (KS-0203 depends on this).
    gov = next(m for m in mappings if m.control.id == "CTL-GOV-01")
    assert gov.modalities == set(Modality)
