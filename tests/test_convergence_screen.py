"""The convergence hero screen (M2-0n) — light asserts behind the visual review.

A hero is reviewed by LOOKING at it (the exec-plan screenshots); these tests guard the
contract the eye can't check every run: the figure is DERIVED from the `RunResult.
convergence` block (REGISTERED_MAPPINGS, never hardcoded — add a mapping and it appears),
the VIOLATE→SATISFIED state shown matches the DERIVED state (change the before/after
numbers → the rendered state changes), the DPDP boundary renders as a deliberate result
(not an empty slot), the disclaimer is ON the screen, and colour comes from the tokens.
"""

from __future__ import annotations

from keystone.demo import (
    ConvergenceMappingView,
    RunResult,
    build_run_result,
    load_recorded_run,
)
from keystone.ui import tokens as T
from keystone.ui.convergence_screen import convergence_html, convergence_svg


def _fixture() -> RunResult:
    return load_recorded_run()


def test_convergence_renders_the_real_values() -> None:
    r = _fixture()
    svg = convergence_svg(r)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    # Every mapping's obligation id is on the figure — derived from the convergence block.
    for m in r.convergence.mappings:
        assert m.obligation_id in svg
    # The throughline (same seam transaction) + the headline claim.
    assert r.binding.transaction_id in svg
    assert "Violated, then satisfied" in svg
    # The cross-jurisdiction modality spread is legible (hard law + advisory).
    assert "HARD LAW" in svg and "ADVISORY" in svg


def test_state_flip_shown_matches_the_derived_state() -> None:
    # The rendered VIOLATED/SATISFIED + the before/after numbers come from the data, not
    # hardcoded: doctor the numbers and the rendered figures follow.
    r = _fixture()
    primary = next(m for m in r.convergence.mappings if m.kind == "EVIDENCED")
    assert f"{primary.before_fails} / {primary.prompt_cap}" in convergence_svg(r)

    doctored_mappings = tuple(
        m.model_copy(update={"before_fails": 7}) if m is primary else m
        for m in r.convergence.mappings
    )
    doctored = r.model_copy(
        update={
            "convergence": r.convergence.model_copy(
                update={"mappings": doctored_mappings}
            )
        }
    )
    assert f"7 / {primary.prompt_cap}" in convergence_svg(doctored)


def test_convergence_is_derived_not_hardcoded() -> None:
    # Add a synthetic mapping; the figure must reflect IT — nothing hardcoded to the
    # real obligation ids.
    r = _fixture()
    extra = ConvergenceMappingView(
        obligation_id="OBL-SENTINEL-001",
        obligation_label="Sentinel Instrument · s. 1 — Sentinel requirement",
        jurisdiction="EU",
        modality="HARD_LAW",
        modality_label="hard law",
        requirement="sentinel requirement text",
        reason="sentinel reason — this event evidences the sentinel obligation.",
        kind="EVIDENCED",
        pre_state="VIOLATE",
        post_state="SATISFY",
        before_fails=9,
        after_fails=0,
        prompt_cap=12,
    )
    doctored = r.model_copy(
        update={
            "convergence": r.convergence.model_copy(
                update={"mappings": (*r.convergence.mappings, extra)}
            )
        }
    )
    svg = convergence_svg(doctored)
    assert "OBL-SENTINEL-001" in svg


def test_boundary_renders_as_a_deliberate_result_not_empty() -> None:
    svg = convergence_svg(_fixture())
    assert "BOUNDARY · NOT EVIDENCED" in svg
    assert "OBL-DPDPA-008" in svg  # the real DPDP obligation, shown — not an empty slot
    assert "▮" not in svg  # nothing on the figure degraded to a placeholder


def test_disclaimer_is_on_the_screen() -> None:
    svg = convergence_svg(_fixture())
    # The honest framing is a credibility asset, ON the screen (a locked decision).
    assert "qualified auditor" in svg
    assert "NOT a legal" in svg  # a phrase from the EVIDENCE_DISCLAIMER itself


def test_screen_draws_colour_from_the_shared_tokens() -> None:
    svg = convergence_svg(_fixture())
    assert T.BERRY in svg  # the VIOLATED (before) state
    assert T.NVIDIA_GREEN in svg  # the SATISFIED (after) state — the patch
    assert T.AMBER in svg  # the strongest-case panel / the boundary
    assert T.INK in svg
    assert T.GOOGLE_FONTS_HREF in svg


def test_no_run_renders_an_honest_empty_state() -> None:
    svg = convergence_svg(None)
    assert svg.startswith("<svg")
    assert "No convergence to show" in svg
    assert "OBL-" not in svg  # nothing fabricated on an empty screen


def test_live_run_builds_the_convergence_without_error() -> None:
    svg = convergence_svg(build_run_result())
    assert "Violated, then satisfied" in svg
    assert svg.startswith("<svg") and svg.endswith("</svg>")


def test_convergence_html_wraps_svg_with_the_font_system() -> None:
    html = convergence_html(_fixture())
    assert "<style>" in html and T.GOOGLE_FONTS_HREF in html
    assert "<svg" in html
