"""The jurisdiction-contrast hero (KS-0502) — light asserts behind the visual review.

Guards what the eye can't check every run: the screen reads the EU/India modality
contrast AND both regulator renderings from the `keystone.demo.RunResult` (never
hardcoded), draws colour from the shared `keystone.ui.tokens`, frames India with
respect (not "behind"), and degrades honestly (▮ / empty state).
"""

from __future__ import annotations

import json
from pathlib import Path

from keystone.demo import RunResult, build_run_result, load_run_result
from keystone.ui import tokens as T
from keystone.ui.jurisdiction_screen import jurisdiction_html, jurisdiction_svg
from keystone.ui.svg import MISSING

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seam_run_result.json"


def _fixture() -> RunResult:
    return load_run_result(_FIXTURE)


def test_renders_the_real_modality_contrast_and_both_formats() -> None:
    r = _fixture()
    svg = jurisdiction_svg(r)

    # Half 1: the EU hard-law vs India self-cert contrast, read from the run-result.
    assert "HARD LAW" in svg and "SELF-CERTIFICATION" in svg
    assert r.ai_security.regulatory.eu_obligation_id in svg
    assert r.ai_security.regulatory.india_obligation_id in svg
    # Half 2: BOTH regulator formats, with their distinct field shapes.
    assert "FINnet" in svg and "goAML" in svg
    assert "transaction_id" in svg  # FINnet field name
    assert "transactionnumber" in svg  # goAML field name
    # The shared risk both halves reference.
    assert r.binding.transaction_id in svg


def test_values_are_read_from_the_run_result_not_hardcoded() -> None:
    # Flip the modality to its opposite; the label must follow the data.
    r = _fixture()
    swapped = r.model_copy(
        update={
            "ai_security": r.ai_security.model_copy(
                update={
                    "regulatory": r.ai_security.regulatory.model_copy(
                        update={"eu_modality": "SELF_CERTIFICATION"}
                    )
                }
            )
        }
    )
    # With EU flipped to self-cert, both governance sides now read self-cert.
    assert jurisdiction_svg(swapped).count("SELF-CERTIFICATION") >= 2


def test_screen_draws_colour_from_the_shared_tokens() -> None:
    svg = jurisdiction_svg(_fixture())
    assert T.TEAL in svg  # governance (both jurisdictions)
    assert T.AMBER in svg  # the shared risk
    assert T.NVIDIA_GREEN in svg  # Keystone's own output (one fact model)
    assert T.INK in svg
    assert T.GOOGLE_FONTS_HREF in svg


def test_india_is_framed_with_respect_not_as_deficient() -> None:
    # Locked framing: India's approach is the HARDER engineering problem, a
    # deliberate choice — never "behind"/"worse"/"deficient"/"lagging".
    svg_text = jurisdiction_svg(_fixture()).lower()
    assert "harder" in svg_text
    for slur in ("behind", "worse", "deficient", "lagging", "immature", "inferior"):
        assert slur not in svg_text


def test_missing_field_degrades_to_placeholder_not_fake_data() -> None:
    raw = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    raw["ai_security"]["regulatory"]["eu_modality"] = ""
    degraded = RunResult.model_validate(raw)
    svg = jurisdiction_svg(degraded)
    assert MISSING in svg
    assert svg.startswith("<svg")


def test_no_run_renders_an_honest_empty_state() -> None:
    svg = jurisdiction_svg(None)
    assert svg.startswith("<svg")
    assert "No run to show" in svg
    assert "TXN-" not in svg


def test_live_run_builds_the_screen() -> None:
    svg = jurisdiction_svg(build_run_result())
    assert "HARD LAW" in svg and svg.endswith("</svg>")


def test_html_wraps_svg_with_the_font_system() -> None:
    html = jurisdiction_html(_fixture())
    assert "<style>" in html and T.GOOGLE_FONTS_HREF in html and "<svg" in html
