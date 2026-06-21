"""Shared SVG primitives for the Phase-5 hero screens — one rendering vocabulary.

The seam hero (KS-0501) and the jurisdiction hero (KS-0502) — and the KS-0503 shell
— build hand-composed SVG from the SAME helpers here, drawing colour/type from
`keystone.ui.tokens`. Keeping these in one place (not copied per screen) is what
makes the screens read as one product. Pure string building: no Streamlit import, so
any screen can be exported standalone for visual QA.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

from . import tokens as T

# Honest emptiness — shown for any field a run-result didn't supply (never faked).
MISSING = "▮▮▮▮▮"


class TextStyle(NamedTuple):
    """A bundled type treatment, so `text()` stays a 4-argument helper."""

    size: int
    fill: str = T.TEXT
    family: str = T.STACK_BODY
    weight: int = 400
    anchor: str = "start"
    spacing: float = 0.0


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def val(value: object) -> tuple[str, bool]:
    """Return (display-text, is_missing). Empty/None → the ▮ placeholder."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return MISSING, True
    return str(value), False


def money(amount: float | None, currency: str | None) -> str:
    if amount is None or currency is None:
        return MISSING
    return f"${amount:,.2f} {currency}"


def wrap(text: str, width: int) -> list[str]:
    """Greedy word-wrap to `width` chars (manual layout — SVG has no flow)."""
    words, out, line = text.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            out.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        out.append(line)
    return out


def text(x: float, y: float, s: str, style: TextStyle) -> str:
    sp = f' letter-spacing="{style.spacing}"' if style.spacing else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{style.family}" '
        f'font-size="{style.size}" font-weight="{style.weight}" fill="{style.fill}" '
        f'text-anchor="{style.anchor}"{sp}>{esc(s)}</text>'
    )


def lines(
    x: float, y: float, rows: Iterable[str], leading: int, style: TextStyle
) -> str:
    return "".join(text(x, y + i * leading, row, style) for i, row in enumerate(rows))


def pill(x: float, y: float, label: str, color: str) -> str:
    """A small layer tag: a colour dot + a letter-spaced mono kicker."""
    return f'<circle cx="{x + 4:.1f}" cy="{y - 4:.1f}" r="4" fill="{color}"/>' + text(
        x + 16,
        y,
        label,
        TextStyle(T.TYPE_SCALE["eyebrow"], color, T.STACK_MONO, 600, spacing=1.6),
    )


def document(body: str, *, width: int, height: int, label: str) -> str:
    """Wrap composed parts in a self-contained SVG (fonts embedded for export)."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="100%" role="img" aria-label="{esc(label)}">'
        f"<defs><style>@import url('{T.GOOGLE_FONTS_HREF}');</style></defs>"
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{T.INK}"/>'
        f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
        f'fill="none" stroke="{T.HAIRLINE}"/>'
        f"{body}</svg>"
    )
