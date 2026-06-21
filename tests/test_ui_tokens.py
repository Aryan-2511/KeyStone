"""The shared design system (KS-0501 Sub-step A) — one source of truth, no drift.

`keystone.ui.tokens` is authoritative for colour/type/spacing. `.streamlit/config.toml`
is a static mirror Streamlit reads at startup; this module mechanically asserts the two
never diverge (the fix for the cross-screen consistency concern).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from keystone.ui import tokens

_CONFIG_TOML = Path(__file__).resolve().parents[1] / ".streamlit" / "config.toml"
_HEX = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")


def test_streamlit_config_mirrors_the_tokens() -> None:
    config = tomllib.loads(_CONFIG_TOML.read_text(encoding="utf-8"))
    assert config["theme"] == tokens.streamlit_theme()


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
