"""The shared design system (KS-0501 Sub-step A) — one source of truth, no drift.

`keystone.ui.tokens` is authoritative for colour/type/spacing. `.streamlit/config.toml`
is a static mirror Streamlit reads at startup; this module mechanically asserts the two
never diverge (the fix for the cross-screen consistency concern).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from keystone.demo import load_recorded_run
from keystone.ui import svg, tokens
from keystone.ui.convergence_screen import convergence_html
from keystone.ui.embed import SEAMLESS_CSS
from keystone.ui.jurisdiction_screen import jurisdiction_html
from keystone.ui.matrix_screen import matrix_html
from keystone.ui.seam_screen import seam_html

_CONFIG_TOML = Path(__file__).resolve().parents[1] / ".streamlit" / "config.toml"
_HEX = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")


def test_streamlit_config_mirrors_the_tokens() -> None:
    config = tomllib.loads(_CONFIG_TOML.read_text(encoding="utf-8"))
    assert config["theme"] == tokens.streamlit_theme()


def test_one_background_token_across_theme_svg_and_iframe() -> None:
    # UI-01: the Streamlit page background, every hero SVG canvas, and every embedded
    # iframe surface are ONE token (INK) — so the heroes sit FLUSH and the "pasted
    # picture" seam can't silently return.
    ink = tokens.INK
    # 1) the page background IS the token (and config mirrors it, asserted above).
    assert tokens.streamlit_theme()["backgroundColor"] == ink
    # 2) the shared SVG canvas fills with the token, with NO outer frame border (the
    # 1px hairline rect that read as a pasted-picture edge is gone).
    doc = svg.document("", width=100, height=100, label="t")
    assert f'fill="{ink}"' in doc
    assert f'stroke="{tokens.HAIRLINE}"' not in doc  # no full-frame border
    # 3) every hero's iframe document uses the token as its surface (== the page).
    r = load_recorded_run()
    for html in (
        seam_html(r),
        jurisdiction_html(r),
        matrix_html(r),
        convergence_html(r),
    ):
        assert f"background:{ink}" in html
    # 4) the iframe-chrome reset references the token (iframe surface == the page).
    assert ink in SEAMLESS_CSS


def test_palette_values_are_valid_hex() -> None:
    for name, value in tokens.PALETTE.items():
        assert _HEX.match(value), f"{name}={value!r} is not a hex colour"


def test_layer_semantics_draw_from_the_palette() -> None:
    # Every layer/seam colour is one of the named palette values — a layer is never
    # coloured by a hand-picked hex on a screen.
    palette_values = set(tokens.PALETTE.values())
    for layer, color in tokens.LAYER_COLOR.items():
        assert color in palette_values, f"{layer} colour {color} not in PALETTE"
    # The semantics the brief pins down.
    assert tokens.LAYER_COLOR["L2"] == tokens.PURPLE
    assert tokens.LAYER_COLOR["L1"] == tokens.BERRY
    assert tokens.LAYER_COLOR["seam"] == tokens.AMBER
    assert tokens.LAYER_COLOR["brand"] == tokens.NVIDIA_GREEN


def test_type_system_is_not_streamlit_default() -> None:
    # A deliberate display + body + mono trio (per the design skill), not defaults.
    assert tokens.FONT_DISPLAY == "Space Grotesk"
    assert tokens.FONT_MONO == "IBM Plex Mono"
    assert "Space+Grotesk" in tokens.GOOGLE_FONTS_HREF
    assert "IBM+Plex+Mono" in tokens.GOOGLE_FONTS_HREF
    assert tokens.GOOGLE_FONTS_HREF in tokens.fonts_css()
