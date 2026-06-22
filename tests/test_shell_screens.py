"""The KS-0503 supporting views — light asserts behind the visual review.

Guard that the ledger / posture / before-after views read real `keystone.demo`
RunResult values (not hardcoded), draw colour from the shared `keystone.ui.tokens`,
and degrade honestly (empty state) — the same discipline as the heroes.
"""

from __future__ import annotations

import json
from pathlib import Path

from keystone.demo import RunResult, load_run_result
from keystone.ui import shell_screens as views
from keystone.ui import tokens as T

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seam_run_result.json"


def _fixture() -> RunResult:
    return load_run_result(_FIXTURE)


def test_ledger_view_renders_the_real_arc_and_chain() -> None:
    r = _fixture()
    svg = views.ledger_svg(r)
    for stage in r.arc.stages:
        assert stage.replace("_", " ").upper() in svg
    assert "chain verified" in svg
    assert f"{r.arc.entry_count} entries" in svg
    # a real entry hash prefix is shown (the evidence feel)
    assert r.arc.entries[0].entry_hash[:10] in svg


def test_posture_view_reads_all_three_layers_from_the_run_result() -> None:
    r = _fixture()
    svg = views.posture_svg(r)
    assert r.ai_security.regulatory.eu_obligation_id in svg  # L3
    assert r.ai_security.regulatory.india_obligation_id in svg
    assert r.financial_crime.typology in svg  # L1
    # L2 before/after probe counts, from the referenced assurance
    a = r.ai_security.assurance
    assert f"{a.before_fails}/{a.prompt_cap}" in svg
    assert f"{a.after_fails}/{a.prompt_cap}" in svg


def test_before_after_view_shows_the_real_referenced_numbers() -> None:
    r = _fixture()
    a = r.ai_security.assurance
    svg = views.before_after_svg(r)
    assert f"{a.before_fails} / {a.prompt_cap}" in svg
    assert f"{a.after_fails} / {a.prompt_cap}" in svg
    assert "blocked by Guardrails" in svg


def test_before_after_follows_the_data_not_hardcoded() -> None:
    # Doctor the assurance counts; the view must reflect THEM (proves not hardcoded).
    raw = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    raw["ai_security"]["assurance"]["before_fails"] = 7
    raw["ai_security"]["assurance"]["prompt_cap"] = 9
    doctored = RunResult.model_validate(raw)
    svg = views.before_after_svg(doctored)
    assert "7 / 9" in svg
    assert "10 / 12" not in svg


def test_views_draw_colour_from_the_shared_tokens() -> None:
    r = _fixture()
    posture = views.posture_svg(r)
    assert T.TEAL in posture and T.PURPLE in posture and T.BERRY in posture
    assert T.GOOGLE_FONTS_HREF in views.ledger_svg(r)
    assert T.INK in views.before_after_svg(r)


def test_views_render_an_honest_empty_state_with_no_run() -> None:
    for builder in (views.ledger_svg, views.posture_svg, views.before_after_svg):
        svg = builder(None)
        assert svg.startswith("<svg")
        assert "No run to show" in svg
