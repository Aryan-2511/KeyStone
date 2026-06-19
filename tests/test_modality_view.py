"""Tests for the modality-contrast view-model (KS-0203).

There is no UI to eyeball, so correctness lives here. The FAST gate fakes the
phrasing backend — NO network, NO key, NO credits — exactly like KS-0204's fast
tests; any live-phrasing assertion would be `-m slow` (none needed here). The
view-model is pure data shaping over the KS-0202 crosswalk + guarded phrasing:
deterministic, byte-identical core data, and the thesis (a real control carrying
the modality contrast) is asserted as a `milestone`.
"""

from __future__ import annotations

import pytest

from keystone.core.controls import ControlMapping, build_crosswalk, load_controls
from keystone.core.controls.loader import DATA_PATH as CONTROLS_DATA_PATH
from keystone.core.controls.models import Control
from keystone.core.obligations import Modality, Obligation, load_obligations
from keystone.core.obligations.loader import DATA_PATH as OBLIGATIONS_DATA_PATH
from keystone.llm import phrase_summary
from keystone.ui.modality_view import (
    ControlView,
    JurisdictionMix,
    ModalityMix,
    build_modality_view,
    contrast_controls,
)

# The contrast controls the crosswalk is expected to surface (KS-0202 data).
GOVERNANCE = "CTL-GOV-01"
TRANSPARENCY = "CTL-TRANSP-01"
HARD_LAW_ONLY = "CTL-RISK-01"  # EU-only, HARD_LAW only


# --- fake backends (no network) ----------------------------------------------


class _EchoBackend:
    """Faithful phrasing: echoes the prompt, so the guard sees no modal drift."""

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        return prompt


class _MapBackend:
    """Returns a canned reply per prompt — lets a test force selective fallback."""

    def __init__(self, replies: dict[str, str]) -> None:
        self.replies = replies

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        return self.replies[prompt]


# --- fixtures -----------------------------------------------------------------


@pytest.fixture(scope="module")
def crosswalk() -> list[ControlMapping]:
    return build_crosswalk(load_controls(), load_obligations())


@pytest.fixture
def view(crosswalk: list[ControlMapping]) -> list[ControlView]:
    return build_modality_view(crosswalk, backend=_EchoBackend())


def _by_id(views: list[ControlView], control_id: str) -> ControlView:
    return next(v for v in views if v.control.id == control_id)


# --- determinism --------------------------------------------------------------


def test_build_is_deterministic(crosswalk: list[ControlMapping]) -> None:
    first = build_modality_view(crosswalk, backend=_EchoBackend())
    second = build_modality_view(crosswalk, backend=_EchoBackend())
    assert first == second  # frozen dataclasses → structural equality


def test_control_order_follows_crosswalk(
    crosswalk: list[ControlMapping], view: list[ControlView]
) -> None:
    assert [v.control.id for v in view] == [m.control.id for m in crosswalk]


def test_obligation_order_within_control_is_sorted_by_id(
    view: list[ControlView],
) -> None:
    for control_view in view:
        ids = [o.id for o in control_view.obligations]
        assert ids == sorted(ids)


# --- modality summary + contrast flag -----------------------------------------


def test_hard_law_only_control_summarises_as_hard_law(view: list[ControlView]) -> None:
    risk = _by_id(view, HARD_LAW_ONLY)
    assert risk.modalities == frozenset({Modality.HARD_LAW})
    assert risk.modality_mix is ModalityMix.HARD_LAW
    assert risk.jurisdiction_mix is JurisdictionMix.EU  # EU-only control
    assert risk.has_modality_contrast is False


def test_india_self_certification_only_control_summarises_atomically() -> None:
    # No shipped control is SELF_CERTIFICATION-only or INDIA-only on its own, so a
    # synthetic one exercises the atomic (non-BOTH) mix branches.
    control = Control.model_validate(
        {
            "id": "CTL-SCERT-01",
            "title": "Self-certification only",
            "description": "Synthetic SELF_CERTIFICATION / INDIA-only control.",
            "spine": [{"framework": "NIST_AI_RMF", "reference": "GOVERN-1.1"}],
        }
    )
    obligation = Obligation.model_validate(
        {
            "id": "OBL-RBI-001",
            "instrument": "RBI_GUIDANCE",
            "citation": {
                "instrument": "RBI_GUIDANCE",
                "provision": "Sutra — Trust is the Foundation",
                "title": "Trust",
            },
            "summary": "Entities are encouraged to act as trusted stewards.",
            "enforcement_modality": "SELF_CERTIFICATION",
            "jurisdiction": "INDIA",
            "control_ids": ["CTL-SCERT-01"],
        }
    )
    [control_view] = build_modality_view(
        build_crosswalk([control], [obligation]), backend=_EchoBackend()
    )
    assert control_view.modality_mix is ModalityMix.SELF_CERTIFICATION
    assert control_view.jurisdiction_mix is JurisdictionMix.INDIA
    assert control_view.has_modality_contrast is False


def test_governance_control_carries_the_contrast(view: list[ControlView]) -> None:
    gov = _by_id(view, GOVERNANCE)
    assert gov.has_modality_contrast is True
    assert gov.modality_mix is ModalityMix.BOTH
    assert gov.modalities == frozenset({Modality.HARD_LAW, Modality.SELF_CERTIFICATION})
    assert gov.jurisdiction_mix is JurisdictionMix.BOTH


def test_transparency_control_carries_the_contrast(view: list[ControlView]) -> None:
    transp = _by_id(view, TRANSPARENCY)
    assert transp.has_modality_contrast is True
    assert transp.modality_mix is ModalityMix.BOTH


def test_contrast_filter_returns_only_contrast_controls(
    view: list[ControlView],
) -> None:
    contrast = contrast_controls(view)
    assert [v.control.id for v in contrast] == [GOVERNANCE, TRANSPARENCY]
    assert all(v.has_modality_contrast for v in contrast)


# --- coverage / no orphans (mirror the KS-0202 invariants at the view level) ---


def test_every_control_appears_exactly_once(
    crosswalk: list[ControlMapping], view: list[ControlView]
) -> None:
    view_ids = [v.control.id for v in view]
    assert sorted(view_ids) == sorted(m.control.id for m in crosswalk)
    assert len(view_ids) == len(set(view_ids))  # no duplicates


def test_every_obligation_appears_under_each_of_its_controls(
    view: list[ControlView],
) -> None:
    # Expected (control_id, obligation_id) edges straight from the source data.
    expected = {(cid, o.id) for o in load_obligations() for cid in o.control_ids}
    actual = {(v.control.id, ob.id) for v in view for ob in v.obligations}
    assert actual == expected  # no missing edges, no orphans


# --- guarded summary plumbed through ------------------------------------------


def test_display_summary_and_fell_back_are_plumbed_from_phrasing(
    view: list[ControlView],
) -> None:
    obligations = {o.id: o for o in load_obligations()}
    for control_view in view:
        for ob_view in control_view.obligations:
            expected = phrase_summary(obligations[ob_view.id], backend=_EchoBackend())
            assert ob_view.display_summary == expected.text
            assert ob_view.fell_back == expected.fell_back


def test_fell_back_flag_preserved_per_obligation() -> None:
    control = Control.model_validate(
        {
            "id": "CTL-TST-01",
            "title": "Test control",
            "description": "Synthetic control for the view-model test.",
            "spine": [{"framework": "ISO_42001", "reference": "A.1"}],
        }
    )
    drifts = _obl("OBL-EUAI-009", "Systems shall log events.")
    faithful = _obl("OBL-EUAI-012", "Systems shall retain records.")
    crosswalk = build_crosswalk([control], [drifts, faithful])
    # The HARD_LAW source phrased advisory must fall back; the binding reword passes.
    backend = _MapBackend(
        {
            "Systems shall log events.": "Systems may log events.",
            "Systems shall retain records.": "Systems must retain records.",
        }
    )

    [control_view] = build_modality_view(crosswalk, backend=backend)
    drift_view, faithful_view = control_view.obligations

    assert drift_view.id == "OBL-EUAI-009"
    assert drift_view.fell_back is True
    assert drift_view.display_summary == "Systems shall log events."  # curated source

    assert faithful_view.id == "OBL-EUAI-012"
    assert faithful_view.fell_back is False
    assert faithful_view.display_summary == "Systems must retain records."


def _obl(obl_id: str, summary: str) -> Obligation:
    return Obligation.model_validate(
        {
            "id": obl_id,
            "instrument": "EU_AI_ACT",
            "citation": {
                "instrument": "EU_AI_ACT",
                "provision": "Art. 9",
                "title": "Risk management system",
            },
            "summary": summary,
            "enforcement_modality": "HARD_LAW",
            "jurisdiction": "EU",
            "control_ids": ["CTL-TST-01"],
        }
    )


# --- a control with no obligations summarises as no mix -----------------------


def test_control_without_obligations_has_no_mix() -> None:
    control = Control.model_validate(
        {
            "id": "CTL-EMPTY-01",
            "title": "Unmapped control",
            "description": "A control no obligation references yet.",
            "spine": [{"framework": "NIST_AI_RMF", "reference": "GOVERN-1.1"}],
        }
    )
    [control_view] = build_modality_view(
        build_crosswalk([control], []), backend=_EchoBackend()
    )
    assert control_view.obligations == ()
    assert control_view.modality_mix is None
    assert control_view.jurisdiction_mix is None
    assert control_view.has_modality_contrast is False


# --- no mutation (MANDATORY) --------------------------------------------------


def test_build_does_not_mutate_core_data_files(crosswalk: list[ControlMapping]) -> None:
    obligations_before = OBLIGATIONS_DATA_PATH.read_bytes()
    controls_before = CONTROLS_DATA_PATH.read_bytes()

    build_modality_view(crosswalk, backend=_EchoBackend())

    assert OBLIGATIONS_DATA_PATH.read_bytes() == obligations_before
    assert CONTROLS_DATA_PATH.read_bytes() == controls_before


# --- milestone: the thesis is present in the SHIPPED data ----------------------


@pytest.mark.milestone
def test_shipped_crosswalk_has_at_least_one_modality_contrast() -> None:
    view = build_modality_view(
        build_crosswalk(load_controls(), load_obligations()), backend=_EchoBackend()
    )
    contrast = contrast_controls(view)
    assert contrast, "no control carries the EU-hard-law vs India-self-cert contrast"
    # Each contrast control must genuinely span both modalities.
    for control_view in contrast:
        assert control_view.modalities == frozenset(
            {Modality.HARD_LAW, Modality.SELF_CERTIFICATION}
        )
