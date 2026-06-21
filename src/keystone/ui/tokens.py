"""The shared design system — ONE source of truth for the Phase-5 UI.

Both the Streamlit shell theme (`.streamlit/config.toml`) and the custom-SVG hero
screens (KS-0501 seam, KS-0502 jurisdiction, KS-0503 shell) draw their colour, type
and spacing from THIS module — so the chrome and the hand-drawn evidence panels read
as one designed surface, with no drift. `.streamlit/config.toml` mirrors the colours
here; `tests/test_ui_tokens.py` fails if the two ever diverge.

Design intent (an audit / evidence artifact, not a dashboard):
- Palette reuses the pitch-deck's, for demo coherence. NVIDIA green is the brand
  anchor, used sparingly; the layer semantics carry meaning — teal = L3, purple =
  L2 / AI-security, berry = L1 / financial-crime, amber = the seam / the target.
  The surface is a near-dark "ledger" so colour and mono ids read as evidence.
- Type is a deliberate trio, NOT the Streamlit defaults: Space Grotesk (a technical
  grotesque) for display, Inter for body, and IBM Plex Mono as the utility/data face
  — monospaced TXN-/ACC- ids and signatures are what make the screen read as proof.
"""

from __future__ import annotations

# --- Palette (4–6 meaning-bearing values + the surface ramp) ------------------
# Brand anchor — NVIDIA green. Sparing: brand mark, "verified" ticks, focus.
NVIDIA_GREEN = "#76B900"

# Layer semantics — each colour IS a layer; never decorative.
TEAL = "#008564"  # L3 — controls / obligations (reserved; little used on the seam)
PURPLE = "#5D1682"  # L2 — AI-security (the assurance loop / prompt-injection world)
BERRY = "#890C58"  # L1 — financial-crime (FATF / AML world)
AMBER = "#B56A00"  # seam / target — the one transaction both worlds land on

# Surface ramp — a near-dark evidence ledger, deepest where the proof sits.
INK = "#0E0F12"  # the deepest panel — the SVG/evidence canvas
PANEL = "#14171C"  # near-dark panel — Streamlit secondary background
BG = "#1A1A1A"  # page background (the deck's dark)
HAIRLINE = "#2A2D34"  # 1px rules / borders on the dark surface
MUTED = "#5E5E5E"  # muted ink — de-emphasised labels, disabled
TEXT_DIM = "#9BA0A6"  # secondary text on dark
TEXT = "#ECEDEE"  # primary text on dark

# Tints used only as low-alpha washes behind a layer's panel (kept here so the wash
# is part of the system, not invented per screen). Hex with alpha (#RRGGBBAA).
PURPLE_WASH = "#5D168226"
BERRY_WASH = "#890C5826"
AMBER_WASH = "#B56A0033"
TEAL_WASH = "#00856422"  # L3 / governance panels (KS-0502)
GREEN_WASH = "#76B90022"  # Keystone's own output panels (KS-0502)

# A near-black warm panel behind amber elements (the "evidence ledger" feel under
# the seam/binding and the shared-risk strip).
AMBER_PANEL = "#19130C"

#: Named palette — the documented set (handy for tests and a legend).
PALETTE: dict[str, str] = {
    "nvidia_green": NVIDIA_GREEN,
    "teal": TEAL,
    "purple": PURPLE,
    "berry": BERRY,
    "amber": AMBER,
    "ink": INK,
    "panel": PANEL,
    "bg": BG,
    "hairline": HAIRLINE,
    "muted": MUTED,
    "text_dim": TEXT_DIM,
    "text": TEXT,
}

#: Which colour speaks for each layer / the seam. The screens read from this so a
#: layer is never coloured by hand.
LAYER_COLOR: dict[str, str] = {
    "L1": BERRY,
    "L2": PURPLE,
    "L3": TEAL,
    "seam": AMBER,
    "brand": NVIDIA_GREEN,
}

# --- Type --------------------------------------------------------------------
FONT_DISPLAY = "Space Grotesk"
FONT_BODY = "Inter"
FONT_MONO = "IBM Plex Mono"

#: Full font stacks (with safe fallbacks) — used in SVG/CSS `font-family`.
STACK_DISPLAY = f"'{FONT_DISPLAY}', 'Inter', system-ui, sans-serif"
STACK_BODY = f"'{FONT_BODY}', system-ui, -apple-system, sans-serif"
STACK_MONO = f"'{FONT_MONO}', 'SFMono-Regular', ui-monospace, monospace"

#: One Google Fonts request for the whole system (the only web dependency).
GOOGLE_FONTS_HREF = (
    "https://fonts.googleapis.com/css2"
    "?family=Space+Grotesk:wght@500;600;700"
    "&family=Inter:wght@400;500;600"
    "&family=IBM+Plex+Mono:wght@400;500;600"
    "&display=swap"
)

#: Type scale in px (a deliberate, sparse ramp — display down to data labels).
TYPE_SCALE: dict[str, int] = {
    "hero": 42,  # the thesis headline
    "title": 24,  # panel titles
    "subtitle": 17,  # plain-language translation line
    "body": 15,
    "data": 16,  # mono ids / amounts (the evidence)
    "small": 12,
    "eyebrow": 11,  # letter-spaced labels / kickers
}

# --- Spacing (a 4px base scale) ----------------------------------------------
SPACE: dict[str, int] = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 40,
    "2xl": 64,
}

RADIUS = 10  # corner radius for panels / the evidence card


def streamlit_theme() -> dict[str, str]:
    """The `[theme]` values the Streamlit shell uses — mirrored by config.toml.

    `tests/test_ui_tokens.py` asserts `.streamlit/config.toml` equals this, so the
    TOML can stay static while this module remains the single source of truth.
    """
    return {
        "base": "dark",
        "primaryColor": NVIDIA_GREEN,
        "backgroundColor": BG,
        "secondaryBackgroundColor": PANEL,
        "textColor": TEXT,
        "font": "sans-serif",
    }


def fonts_css() -> str:
    """A `<style>` block: import the type system and apply it across the shell.

    Injected once into the Streamlit page (and reused inside the hero HTML wrapper)
    so the chrome and the SVG share the exact same faces.
    """
    return (
        f"@import url('{GOOGLE_FONTS_HREF}');\n"
        "html, body, [class*='css'], .stApp, .stMarkdown {"
        f" font-family: {STACK_BODY}; }}\n"
        "h1, h2, h3, h4, .ks-display {"
        f" font-family: {STACK_DISPLAY}; letter-spacing: -0.01em; }}\n"
        "code, kbd, samp, .ks-mono {"
        f" font-family: {STACK_MONO}; }}\n"
    )
