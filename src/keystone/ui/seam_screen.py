"""The seam hero (KS-0501) — one transaction rendered as TWO failures at once.

The thesis as an image: a single payment (`run_result.seam_transaction`) sits at the
centre as a target; the Layer-2 AI-security finding (purple) and the Layer-1
financial-crime finding (berry) flank it; and the signature element — an amber
convergence where both worlds drop into ONE binding — shows they reference the SAME
transaction id and the SAME canonical signature. Static, designed; the drama is the
composition, not animation.

Every value is read from the `keystone.demo.RunResult` contract — never hardcoded,
never mocked (the "it's real" claim). A missing field degrades to a ▮ placeholder
(honest emptiness), and a missing run-result renders a clear empty state, so the
screen never crashes or shows fabricated data.

Colour, type and spacing come from `keystone.ui.tokens` (the one design system the
Streamlit theme and these SVGs share). Pure string building — no Streamlit import,
so the SVG can also be exported standalone (the visual-QA screenshot).
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import NamedTuple

from keystone.demo import RunResult

from . import tokens as T

# Honest emptiness — shown for any field the run-result didn't supply.
MISSING = "▮▮▮▮▮"

_VIEWBOX_W = 1280
_VIEWBOX_H = 860

# The hero is centred at this max width; the iframe height (for components.html)
# is derived from it so the SVG never clips at its largest rendered size.
_HERO_MAX_WIDTH = 1180
SEAM_HEIGHT_PX = round(_HERO_MAX_WIDTH * _VIEWBOX_H / _VIEWBOX_W) + 18


class TextStyle(NamedTuple):
    """A bundled type treatment, so `_text` stays a 4-argument helper."""

    size: int
    fill: str = T.TEXT
    family: str = T.STACK_BODY
    weight: int = 400
    anchor: str = "start"
    spacing: float = 0.0


# --- small SVG / formatting helpers ------------------------------------------


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _val(value: object) -> tuple[str, bool]:
    """Return (display-text, is_missing). Empty/None → the ▮ placeholder."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return MISSING, True
    return str(value), False


def _money(amount: float | None, currency: str | None) -> str:
    if amount is None or currency is None:
        return MISSING
    return f"${amount:,.2f} {currency}"


def _wrap(text: str, width: int) -> list[str]:
    """Greedy word-wrap to `width` chars (manual layout — SVG has no flow)."""
    words, lines, line = text.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return lines


def _text(x: float, y: float, s: str, style: TextStyle) -> str:
    sp = f' letter-spacing="{style.spacing}"' if style.spacing else ""
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{style.family}" '
        f'font-size="{style.size}" font-weight="{style.weight}" fill="{style.fill}" '
        f'text-anchor="{style.anchor}"{sp}>{_esc(s)}</text>'
    )


def _lines(
    x: float, y: float, rows: Iterable[str], leading: int, style: TextStyle
) -> str:
    return "".join(_text(x, y + i * leading, row, style) for i, row in enumerate(rows))


def _pill(x: float, y: float, label: str, color: str) -> str:
    """A small layer tag: a colour dot + a letter-spaced mono kicker."""
    return f'<circle cx="{x + 4:.1f}" cy="{y - 4:.1f}" r="4" fill="{color}"/>' + _text(
        x + 16,
        y,
        label,
        TextStyle(T.TYPE_SCALE["eyebrow"], color, T.STACK_MONO, 600, spacing=1.6),
    )


def _datum(x: float, y: float, label: str, value: str, *, missing: bool) -> str:
    """A label/value evidence row: a quiet eyebrow over a mono value (or ▮).

    Panels share one width, so the value wraps to a fixed character measure.
    """
    return _text(
        x,
        y,
        label,
        TextStyle(T.TYPE_SCALE["eyebrow"], T.TEXT_DIM, T.STACK_MONO, 500, spacing=1.4),
    ) + _lines(
        x,
        y + 20,
        _wrap(value, 38),
        18,
        TextStyle(13, T.MUTED if missing else T.TEXT, T.STACK_MONO, 500),
    )


# --- the composition ----------------------------------------------------------


def _svg_document(body: str) -> str:
    """Wrap composed parts in the self-contained SVG (fonts embedded for export)."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {_VIEWBOX_W} {_VIEWBOX_H}" '
        f'width="100%" role="img" aria-label="The seam: one transaction, two failures">'
        f"<defs><style>@import url('{T.GOOGLE_FONTS_HREF}');</style></defs>"
        f'<rect x="0" y="0" width="{_VIEWBOX_W}" height="{_VIEWBOX_H}" fill="{T.INK}"/>'
        f'<rect x="0.5" y="0.5" width="{_VIEWBOX_W - 1}" height="{_VIEWBOX_H - 1}" '
        f'fill="none" stroke="{T.HAIRLINE}"/>'
        f"{body}</svg>"
    )


def _empty_state(message: str) -> str:
    cx = _VIEWBOX_W / 2
    cy = _VIEWBOX_H / 2
    body = (
        _text(
            cx,
            cy - 16,
            "No run to show",
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600, "middle"),
        )
        + _text(
            cx,
            cy + 16,
            message,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, anchor="middle"),
        )
        + _text(
            cx,
            cy + 52,
            "▮▮▮▮▮  ▮▮▮▮▮  ▮▮▮▮▮",
            TextStyle(
                T.TYPE_SCALE["data"], T.MUTED, T.STACK_MONO, anchor="middle", spacing=4
            ),
        )
    )
    return _svg_document(body)


def _header() -> str:
    return (
        _pill(48, 56, "KEYSTONE · ASSURANCE & COMPLIANCE", T.NVIDIA_GREEN)
        + _text(
            48,
            104,
            "One transaction. Two independent failures.",
            TextStyle(T.TYPE_SCALE["hero"], T.TEXT, T.STACK_DISPLAY, 700, spacing=-0.5),
        )
        + _text(
            48,
            134,
            "The same payment is a money-laundering crime and an AI-security "
            "breach — each caught on its own.",
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT_DIM),
        )
    )


def _l2_panel(r: RunResult, x: float, w: float, top: float, h: float) -> str:
    ai = r.ai_security
    sig, sig_missing = _val(ai.signature_name)
    owasp, owasp_missing = _val(ai.regulatory.owasp_llm)
    outcome, outcome_missing = _val(ai.outcome.replace("_", " "))
    inner = x + 26
    return (
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.PURPLE_WASH}" stroke="{T.PURPLE}" stroke-opacity="0.55"/>'
        f'<rect x="{x}" y="{top}" width="3" height="{h}" rx="1.5" fill="{T.PURPLE}"/>'
        + _pill(inner, top + 34, "LAYER 2 · AI-SECURITY", T.PURPLE)
        + _text(
            inner,
            top + 78,
            "AI tricked by a hidden memo",
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600),
        )
        + _lines(
            inner,
            top + 108,
            _wrap(
                "A payments agent read instructions hidden in the transaction memo and obeyed them.",
                42,
            ),
            20,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM),
        )
        + f'<line x1="{inner}" y1="{top + 158}" x2="{x + w - 26}" y2="{top + 158}" stroke="{T.HAIRLINE}"/>'
        + _datum(inner, top + 188, "SIGNATURE", sig, missing=sig_missing)
        + _datum(inner, top + 240, "CLASS", f"OWASP {owasp}", missing=owasp_missing)
        + _datum(inner, top + 292, "RESULT", outcome, missing=outcome_missing)
        + f'<circle cx="{inner + 4}" cy="{top + h - 26}" r="4.5" fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            inner + 16,
            top + h - 22,
            "Garak found it · Guardrails patched it",
            TextStyle(T.TYPE_SCALE["small"], T.NVIDIA_GREEN, T.STACK_MONO, 500),
        )
    )


def _l1_panel(r: RunResult, x: float, w: float, top: float, h: float) -> str:
    fc = r.financial_crime
    typ, typ_missing = _val(fc.typology)
    sev, _ = _val(fc.severity)
    signal = fc.signal or {}
    count = signal.get("transfer_count")
    total = signal.get("total_amount")
    window = signal.get("window_minutes")
    if (
        isinstance(count, int | float)
        and isinstance(total, int | float)
        and isinstance(window, int | float)
    ):
        signal_text = (
            f"{int(count)} transfers · ${float(total):,.2f} · {int(window)} min"
        )
        signal_missing = False
    else:
        signal_text, signal_missing = MISSING, True
    inner = x + 26
    return (
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.BERRY_WASH}" stroke="{T.BERRY}" stroke-opacity="0.55"/>'
        f'<rect x="{x + w - 3}" y="{top}" width="3" height="{h}" rx="1.5" fill="{T.BERRY}"/>'
        + _pill(inner, top + 34, "LAYER 1 · FINANCIAL-CRIME", T.BERRY)
        + _text(
            inner,
            top + 78,
            "A money-laundering pattern",
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600),
        )
        + _lines(
            inner,
            top + 108,
            _wrap(
                "Many sub-threshold transfers in minutes — structuring to dodge the reporting limit.",
                42,
            ),
            20,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM),
        )
        + f'<line x1="{inner}" y1="{top + 158}" x2="{x + w - 26}" y2="{top + 158}" stroke="{T.HAIRLINE}"/>'
        + _datum(
            inner, top + 188, "TYPOLOGY (FATF)", f"{typ} · {sev}", missing=typ_missing
        )
        + _datum(inner, top + 240, "SIGNAL", signal_text, missing=signal_missing)
        + _datum(inner, top + 292, "BASIS", "amounts & timing only", missing=False)
        + f'<circle cx="{inner + 4}" cy="{top + h - 26}" r="4.5" fill="{T.BERRY}"/>'
        + _text(
            inner + 16,
            top + h - 22,
            "Memo-blind — caught independently",
            TextStyle(T.TYPE_SCALE["small"], "#D17AAE", T.STACK_MONO, 500),
        )
    )


def _tx_card(r: RunResult, x: float, w: float, top: float, h: float) -> str:
    tx = r.seam_transaction
    tx_id, id_missing = _val(tx.id)
    cx = x + w / 2
    accounts, acct_missing = _val(
        f"{tx.sender_account} → {tx.recipient_account}"
        if tx.sender_account and tx.recipient_account
        else None
    )
    memo, memo_missing = _val(tx.memo)
    memo_lines = _wrap(memo, 40)
    memo_box_top = top + 188
    memo_box_h = 26 + len(memo_lines) * 17
    tick = 12
    corners = "".join(
        f'<path d="{d}" stroke="{T.AMBER}" stroke-width="2" fill="none"/>'
        for d in (
            f"M{x} {top + tick} V{top} H{x + tick}",
            f"M{x + w - tick} {top} H{x + w} V{top + tick}",
            f"M{x + w} {top + h - tick} V{top + h} H{x + w - tick}",
            f"M{x + tick} {top + h} H{x} V{top + h - tick}",
        )
    )
    return (
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.AMBER_WASH}" stroke="{T.AMBER}" stroke-width="1.5"/>'
        + corners
        + _text(
            cx,
            top + 34,
            "THE TRANSACTION",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, "middle", 3),
        )
        + _text(
            cx,
            top + 80,
            tx_id,
            TextStyle(
                30, T.MUTED if id_missing else T.TEXT, T.STACK_MONO, 600, "middle"
            ),
        )
        + _text(
            cx,
            top + 116,
            _money(tx.amount, tx.currency),
            TextStyle(20, T.TEXT, T.STACK_MONO, 500, "middle"),
        )
        + _text(
            cx,
            top + 146,
            f"{accounts}  ·  {tx.tx_type}" if not acct_missing else accounts,
            TextStyle(
                13,
                T.MUTED if acct_missing else T.TEXT_DIM,
                T.STACK_MONO,
                anchor="middle",
            ),
        )
        + _text(
            x + 26,
            memo_box_top - 10,
            "MEMO — untrusted data the agent obeyed",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 500, spacing=1.2),
        )
        + f'<rect x="{x + 18}" y="{memo_box_top}" width="{w - 36}" height="{memo_box_h}" '
        f'rx="6" fill="{T.AMBER_WASH}" stroke="{T.AMBER}" stroke-opacity="0.5"/>'
        + _lines(
            x + 30,
            memo_box_top + 22,
            memo_lines,
            17,
            TextStyle(12, T.MUTED if memo_missing else "#E7B973", T.STACK_MONO, 500),
        )
    )


def _connectors(panel_bottom: float, bar_top: float) -> str:
    """Three lines — L2 (purple), TX (amber), L1 (berry) — pour into the binding.

    The convergence node where they meet is the signature moment: two worlds, one
    thing. It sits on the binding bar's top edge.
    """
    node_x = _VIEWBOX_W / 2
    drop = bar_top
    out = []
    for sx, color in ((234.0, T.PURPLE), (1046.0, T.BERRY)):
        midy = (panel_bottom + drop) / 2
        out.append(
            f'<path d="M{sx:.1f} {panel_bottom:.1f} '
            f'C{sx:.1f} {midy:.1f} {node_x:.1f} {midy:.1f} {node_x:.1f} {drop:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="2.5" stroke-opacity="0.9"/>'
            f'<circle cx="{sx:.1f}" cy="{panel_bottom:.1f}" r="4" fill="{color}"/>'
        )
    out.append(
        f'<line x1="{node_x:.1f}" y1="{panel_bottom:.1f}" x2="{node_x:.1f}" y2="{drop:.1f}" '
        f'stroke="{T.AMBER}" stroke-width="3"/>'
    )
    s = 11
    out.append(
        f'<circle cx="{node_x:.1f}" cy="{drop:.1f}" r="20" fill="none" '
        f'stroke="{T.AMBER}" stroke-opacity="0.35"/>'
        f'<path d="M{node_x:.1f} {drop - s:.1f} L{node_x + s:.1f} {drop:.1f} '
        f'L{node_x:.1f} {drop + s:.1f} L{node_x - s:.1f} {drop:.1f} Z" '
        f'fill="{T.AMBER}"/>'
    )
    return "".join(out)


def _binding(r: RunResult, top: float) -> str:
    """The signature element: two worlds drop into ONE shared id + ONE signature."""
    b = r.binding
    tx_id, id_missing = _val(b.transaction_id)
    sig, sig_missing = _val(b.signature_name)
    thesis, _ = _val(b.thesis)
    thesis = thesis if thesis.endswith(".") else thesis[:1].upper() + thesis[1:] + "."
    bar_x, bar_w, bar_h = 196, 888, 188
    bar_cx = bar_x + bar_w / 2
    chip_w, chip_h = 286, 52
    left_cx, right_cx = bar_cx - 178, bar_cx + 178
    chip_y = top + 64

    def _chip(cx: float, text: str, missing: bool) -> str:
        return (
            f'<rect x="{cx - chip_w / 2}" y="{chip_y}" width="{chip_w}" height="{chip_h}" '
            f'rx="9" fill="{T.INK}" stroke="{T.AMBER}" stroke-width="1.5"/>'
            + _text(
                cx,
                chip_y + 33,
                text,
                TextStyle(
                    19, T.MUTED if missing else T.TEXT, T.STACK_MONO, 600, "middle"
                ),
            )
        )

    small_dim = TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, anchor="middle")
    return (
        f'<rect x="{bar_x}" y="{top}" width="{bar_w}" height="{bar_h}" rx="{T.RADIUS}" '
        f'fill="#19130C" stroke="{T.AMBER}" stroke-width="1.75"/>'
        f'<rect x="{bar_x}" y="{top}" width="{bar_w}" height="3" rx="1.5" fill="{T.AMBER}"/>'
        + _text(
            bar_cx,
            top + 34,
            "THE BINDING · ONE EVENT, TWO FAILURES",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, "middle", 3),
        )
        + _text(left_cx, chip_y - 12, "same transaction", small_dim)
        + _chip(left_cx, tx_id, id_missing)
        + _text(
            bar_cx,
            chip_y + 35,
            "≡",
            TextStyle(36, T.AMBER, T.STACK_DISPLAY, 700, "middle"),
        )
        + _text(right_cx, chip_y - 12, "same signature", small_dim)
        + _chip(right_cx, sig, sig_missing)
        + _text(
            left_cx,
            chip_y + chip_h + 24,
            f"FATF {r.binding.fatf_typology} — Layer 1",
            TextStyle(T.TYPE_SCALE["small"], "#D17AAE", T.STACK_MONO, 500, "middle"),
        )
        + _text(
            right_cx,
            chip_y + chip_h + 24,
            f"OWASP {r.ai_security.regulatory.owasp_llm.split(':')[0]} — Layer 2",
            TextStyle(T.TYPE_SCALE["small"], "#B98BD6", T.STACK_MONO, 500, "middle"),
        )
        + _lines(
            bar_cx,
            top + bar_h - 22,
            _wrap(thesis, 78),
            17,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT, anchor="middle"),
        )
    )


def _footer(r: RunResult) -> str:
    arc = r.arc
    chain = "verified" if arc.chain_verified else "TAMPERED"
    chain_color = T.NVIDIA_GREEN if arc.chain_verified else T.BERRY
    stages = " → ".join(arc.stages) if arc.stages else MISSING
    y = _VIEWBOX_H - 34
    right_text = f"chain {chain} · {arc.entry_count} entries"
    dot_x = _VIEWBOX_W - 48 - 8.4 * len(right_text) - 14
    return (
        f'<line x1="48" y1="{y - 26}" x2="{_VIEWBOX_W - 48}" y2="{y - 26}" stroke="{T.HAIRLINE}"/>'
        + _text(
            48,
            y,
            f"Rendered from a real run · {r.report.report_format} STR "
            f"{r.report.status.lower()} · arc: {stages}",
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO),
        )
        + f'<circle cx="{dot_x:.1f}" cy="{y - 4}" r="4" fill="{chain_color}"/>'
        + _text(
            _VIEWBOX_W - 48,
            y,
            right_text,
            TextStyle(
                T.TYPE_SCALE["small"],
                T.TEXT_DIM if arc.chain_verified else chain_color,
                T.STACK_MONO,
                anchor="end",
            ),
        )
    )


def seam_svg(result: RunResult | None) -> str:
    """The seam hero as a self-contained SVG string, from a `RunResult` (or empty)."""
    if result is None:
        return _empty_state("Run the demo or load a saved run to render the seam.")

    panel_top, panel_h = 168.0, 372.0
    panel_bottom = panel_top + panel_h
    bar_top = 600.0
    body = (
        _header()
        + _l2_panel(result, 48, 372, panel_top, panel_h)
        + _tx_card(result, 466, 348, panel_top, panel_h)
        + _l1_panel(result, 860, 372, panel_top, panel_h)
        + _connectors(panel_bottom, bar_top)
        + _binding(result, bar_top)
        + _footer(result)
    )
    return _svg_document(body)


def seam_html(result: RunResult | None) -> str:
    """A self-contained HTML doc for `components.v1.html` (an iframe).

    Embedded in an iframe (NOT `st.html`, which sanitises inline SVG away) with its
    own font import and an ink background, so the hero renders seamlessly at the
    Streamlit container width, centred up to the hero max width.
    """
    return (
        f"<style>{T.fonts_css()}"
        f"html,body{{margin:0;background:{T.INK};}}"
        f".ks-seam{{max-width:{_HERO_MAX_WIDTH}px;margin:0 auto;}}</style>"
        f'<div class="ks-seam">{seam_svg(result)}</div>'
    )
