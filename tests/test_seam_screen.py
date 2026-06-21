"""The seam hero screen (KS-0501) — light asserts behind the visual review.

A UI screen is reviewed by LOOKING at it (see the exec-plan screenshot); these tests
only guard the contract the eye can't check on every run: that the screen reads its
values from the `keystone.demo.RunResult` (never hardcoded), draws colour from the
shared `keystone.ui.tokens`, and degrades honestly (a ▮ placeholder / empty state)
instead of crashing or inventing data.
"""

from __future__ import annotations

import json
from pathlib import Path

from keystone.demo import RunResult, build_run_result, load_run_result
from keystone.ui import tokens as T
from keystone.ui.seam_screen import MISSING, seam_html, seam_svg

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seam_run_result.json"


def _fixture() -> RunResult:
    return load_run_result(_FIXTURE)


def test_fixture_run_renders_real_seam_values() -> None:
    r = _fixture()
    svg = seam_svg(r)

    # The real seam tx, both findings, and the canonical signature are all present.
    assert r.seam_transaction.id in svg
    assert r.binding.signature_name in svg
    assert r.financial_crime.typology in svg
    assert "LLM01" in svg  # the L2 OWASP class, from the run-result mapping
    assert r.seam_transaction.recipient_account in svg  # the memo's target account


def test_values_are_read_from_the_run_result_not_hardcoded() -> None:
    # Doctor the run-result with sentinels; the SVG must reflect THEM, proving the
    # screen renders from the contract rather than baked-in strings.
    r = _fixture()
    doctored = r.model_copy(
        update={
            "seam_transaction": r.seam_transaction.model_copy(
                update={"id": "TXN-SENTINEL"}
            ),
            "binding": r.binding.model_copy(
                update={
                    "transaction_id": "TXN-SENTINEL",
                    "signature_name": "sig-sentinel",
                }
            ),
        }
    )
    svg = seam_svg(doctored)

    assert "TXN-SENTINEL" in svg
    assert "sig-sentinel" in svg
    assert r.seam_transaction.id not in svg  # the original id is gone


def test_screen_draws_colour_from_the_shared_tokens() -> None:
    svg = seam_svg(_fixture())
    # Layer semantics come from tokens, not hand-picked hexes on the screen.
    assert T.PURPLE in svg  # L2 / AI-security
    assert T.BERRY in svg  # L1 / financial-crime
    assert T.AMBER in svg  # seam / the binding
    assert T.INK in svg  # the evidence canvas
    assert T.GOOGLE_FONTS_HREF in svg  # the shared type system


def test_missing_field_degrades_to_placeholder_not_fake_data() -> None:
    # A saved run with a blanked signature must show the ▮ placeholder, never crash
    # and never fabricate a value.
    raw = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    raw["binding"]["signature_name"] = ""
    degraded = RunResult.model_validate(raw)

    svg = seam_svg(degraded)
    assert MISSING in svg
    assert svg.startswith("<svg")


def test_no_run_renders_an_honest_empty_state() -> None:
    svg = seam_svg(None)
    assert svg.startswith("<svg")
    assert "No run to show" in svg
    # No fabricated transaction/signature on an empty screen.
    assert "TXN-" not in svg


def test_live_run_builds_the_screen_without_error() -> None:
    # The page works live (KS-0500 build) as well as from replay.
    svg = seam_svg(build_run_result())
    assert "TXN-" in svg
    assert svg.startswith("<svg") and svg.endswith("</svg>")


def test_seam_html_wraps_svg_with_the_font_system() -> None:
    html = seam_html(_fixture())
    assert "<style>" in html and T.GOOGLE_FONTS_HREF in html
    assert "<svg" in html
