"""The seam-matrix hero screen (M1-06) — light asserts behind the visual review.

A hero screen is reviewed by LOOKING at it (the exec-plan screenshots); these tests
guard the contract the eye can't check every run: the figure is DERIVED from the
`RunResult.matrix` block (REGISTERED_PAIRS, never hardcoded — add a pair and it
appears), draws colour from the shared `keystone.ui.tokens`, renders the P4 boundary as
a deliberate result (not an empty slot), translates every OWASP/FATF id, and degrades
honestly instead of crashing.
"""

from __future__ import annotations

from keystone.demo import (
    MatrixPairView,
    RunResult,
    build_run_result,
    load_recorded_run,
)
from keystone.ui import tokens as T
from keystone.ui.matrix_screen import MATRIX_CAVEATS, matrix_html, matrix_svg


def _fixture() -> RunResult:
    return load_recorded_run()


def test_matrix_renders_the_real_matrix_values() -> None:
    r = _fixture()
    svg = matrix_svg(r)
    assert svg.startswith("<svg") and svg.endswith("</svg>")
    # Every registered pair's id + OWASP id + FATF typology id is on the figure (the
    # plain-language labels are present too but word-wrap across lines) — derived from
    # the matrix block.
    for p in r.matrix.pairs:
        assert p.pair_id in svg
        assert p.attack_owasp_id in svg
        if p.typology:
            assert p.typology in svg
    # The framework element carries the independence ONCE (its non-wrapped caption).
    assert "ONE FRAMEWORK" in svg
    assert "independence — a property" in svg
    # The characterized boundary is labelled and its statement attached (P4).
    assert "THE BOUNDARY (P4)" in svg
    # The axis grouping (the anti-cherry-pick sampling, made visual).
    assert "AXIS A" in svg and "AXIS B" in svg


def test_matrix_is_derived_from_the_run_not_hardcoded() -> None:
    # Add a synthetic pair to the matrix data; the figure must reflect IT — proving the
    # screen renders whatever pairs the data carries, with nothing hardcoded to P1-P5.
    r = _fixture()
    extra = MatrixPairView(
        pair_id="P9",
        attack_owasp_id="LLM99",
        attack_name="Sentinel attack",
        typology="SENTINEL_TYPOLOGY",
        typology_label="Sentinel typology label",
        result="CLEAN",
        axis="A",
    )
    doctored = r.model_copy(
        update={
            "matrix": r.matrix.model_copy(update={"pairs": (*r.matrix.pairs, extra)})
        }
    )
    svg = matrix_svg(doctored)
    assert "P9" in svg
    assert "LLM99" in svg
    assert "Sentinel typology label" in svg


def test_boundary_pair_renders_as_a_deliberate_result_not_empty() -> None:
    svg = matrix_svg(_fixture())
    # The boundary is an explicit, labelled result — never an empty/missing slot.
    assert "BOUNDARY" in svg
    assert "No money moves" in svg  # the deliberate "by nature, not by gap" result
    assert "▮" not in svg  # nothing on the figure degraded to a placeholder


def test_screen_draws_colour_from_the_shared_tokens() -> None:
    svg = matrix_svg(_fixture())
    assert T.PURPLE in svg  # the attacks (L2 / AI-security)
    assert T.BERRY in svg  # the bound typologies (L1 / financial-crime)
    assert T.AMBER in svg  # the framework / the boundary treatment
    assert T.INK in svg  # the evidence canvas
    assert T.GOOGLE_FONTS_HREF in svg  # the shared type system


def test_no_run_renders_an_honest_empty_state() -> None:
    svg = matrix_svg(None)
    assert svg.startswith("<svg")
    assert "No matrix to show" in svg
    assert "LLM01" not in svg  # nothing fabricated on an empty screen


def test_empty_matrix_block_degrades_to_empty_state() -> None:
    r = _fixture()
    empty = r.model_copy(update={"matrix": r.matrix.model_copy(update={"pairs": ()})})
    svg = matrix_svg(empty)
    assert "No matrix to show" in svg


def test_live_run_builds_the_matrix_without_error() -> None:
    svg = matrix_svg(build_run_result())
    assert "ONE FRAMEWORK" in svg
    assert svg.startswith("<svg") and svg.endswith("</svg>")


def test_matrix_html_wraps_svg_with_the_font_system() -> None:
    html = matrix_html(_fixture())
    assert "<style>" in html and T.GOOGLE_FONTS_HREF in html
    assert "<svg" in html


def test_caveats_exist_for_the_shell_to_surface() -> None:
    # The honest caveats are reachable detail (the shell renders them) — NOT on the hero.
    assert len(MATRIX_CAVEATS) >= 2
    joined = " ".join(MATRIX_CAVEATS)
    assert "P1" in joined and "P5" in joined  # both honest caveats are present
    svg = matrix_svg(_fixture())
    # They must NOT clutter the hero figure itself.
    assert MATRIX_CAVEATS[0] not in svg
