"""The jurisdiction-contrast hero (KS-0502) — the defense is fragmented; we unify it.

Two contrasts, both from the `keystone.demo.RunResult`, anchored on the SAME detected
risk (TXN-000016 / FATF structuring / memo-instruction-injection):

1. ONE RISK, TWO RULEBOOKS — the EU governs it as HARD LAW (binding, fineable) while
   India governs it by SELF-CERTIFICATION (RBI FREE-AI principles — advisory, emerging).
   The modalities are read from the obligation graph, never assumed. India's approach
   is framed with respect: a deliberate, innovation-preserving choice, and the HARDER
   engineering problem (principles, not rulebooks) — never "behind".
2. ONE REPORT, EVERY REGULATOR — the SAME signed STR rendered into FINnet (FIU-IND,
   India) AND goAML (UN, 70+ countries): one fact model, two formats. The matching
   values under different field names make "same facts, different shape" visible.

Signature element: the contrast itself — the world's two different rulebooks set
against Keystone's one source emitting both formats. Inherits the KS-0501 design
system (`keystone.ui.tokens` + `keystone.ui.svg`); static; every value real, with a
▮ placeholder for any missing field and an honest empty state for a missing run.
"""

from __future__ import annotations

from keystone.demo import RunResult

from . import svg
from . import tokens as T
from .svg import MISSING, TextStyle

_VIEWBOX_W = 1280
_VIEWBOX_H = 1060
_HERO_MAX_WIDTH = 1180
# Iframe height for components.html (derived from the viewBox so it never clips).
JURISDICTION_HEIGHT_PX = round(_HERO_MAX_WIDTH * _VIEWBOX_H / _VIEWBOX_W) + 18

_LABEL = "Cross-jurisdiction: one risk, every rulebook and format"

# Token roles ON THIS screen (no new hexes): teal = the governance/obligations world
# (L3) for BOTH jurisdictions — they differ by TREATMENT (solid+filled = hard law;
# dashed+outline = self-cert), not by hue, so neither reads as lesser. Amber = the
# shared risk both reference (the seam tx). NVIDIA green = Keystone's own output (the
# one fact model that emits every format).
_GOV = T.TEAL
_RISK = T.AMBER
_OURS = T.NVIDIA_GREEN
_GOV_WASH = T.TEAL_WASH
_OURS_WASH = T.GREEN_WASH


def _get(d: object, *path: object) -> object:
    """Walk a nested dict/list by keys/indices; None if any step is absent."""
    cur: object = d
    for key in path:
        if isinstance(cur, dict) and isinstance(key, str):
            cur = cur.get(key)
        elif (
            isinstance(cur, list)
            and isinstance(key, int)
            and -len(cur) <= key < len(cur)
        ):
            cur = cur[key]
        else:
            return None
        if cur is None:
            return None
    return cur


def _modality_label(modality: str) -> tuple[str, str]:
    """(big label, plain sub) for an enforcement modality value — presentation only."""
    if modality == "HARD_LAW":
        return "HARD LAW", "binding · enforceable · fineable"
    if modality == "SELF_CERTIFICATION":
        return "SELF-CERTIFICATION", "advisory · principle-based · emerging"
    return MISSING, ""


# --- header + the shared-risk through-line -----------------------------------


def _header() -> str:
    return (
        svg.pill(64, 56, "KEYSTONE · CROSS-JURISDICTION COMPLIANCE", _OURS)
        + svg.text(
            64,
            104,
            "One risk. Every rulebook.",
            TextStyle(T.TYPE_SCALE["hero"], T.TEXT, T.STACK_DISPLAY, 700, spacing=-0.5),
        )
        + svg.text(
            64,
            134,
            "The threat is borderless and identical everywhere — the defense is "
            "fragmented across jurisdictions. Keystone speaks all of them.",
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT_DIM),
        )
    )


def _shared_risk(r: RunResult) -> str:
    """The amber through-line: the ONE risk both halves reference."""
    tx_id, tx_missing = svg.val(r.binding.transaction_id)
    typ, _ = svg.val(r.financial_crime.typology)
    sig, _ = svg.val(r.binding.signature_name)
    x, y, w, h = 240, 168, 800, 70
    cx = x + w / 2
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.AMBER_PANEL}" stroke="{_RISK}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="3" rx="1.5" fill="{_RISK}"/>'
        + svg.text(
            cx,
            y + 26,
            "THE SAME DETECTED RISK — GOVERNED & FILED EVERYWHERE",
            TextStyle(T.TYPE_SCALE["eyebrow"], _RISK, T.STACK_MONO, 600, "middle", 2.5),
        )
        + svg.text(
            cx,
            y + 52,
            f"{tx_id}   ·   FATF {typ}   ·   {sig}",
            TextStyle(
                15, T.MUTED if tx_missing else T.TEXT, T.STACK_MONO, 600, "middle"
            ),
        )
    )


# --- band 1: one risk, two rulebooks (governance) ----------------------------


def _gov_card(box: tuple[float, float, float, float], *, dashed: bool) -> str:
    x, y, w, h = box
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{_GOV_WASH}" stroke="{_GOV}" stroke-width="1.5"{dash}/>'
    )


def _eu_side(r: RunResult, box: tuple[float, float, float, float]) -> str:
    x, y, w, h = box
    inner = x + 28
    big, sub = _modality_label(r.ai_security.regulatory.eu_modality)
    law, law_missing = svg.val(r.ai_security.regulatory.eu_ai_act)
    oid, _ = svg.val(r.ai_security.regulatory.eu_obligation_id)
    return (
        _gov_card(box, dashed=False)
        # filled header strip = binding/authoritative
        + f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="{T.RADIUS}" fill="{_GOV}"/>'
        + f'<rect x="{x}" y="{y + 20}" width="{w}" height="14" fill="{_GOV}"/>'
        + svg.text(
            inner,
            y + 23,
            "EUROPEAN UNION",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.INK, T.STACK_MONO, 700, spacing=2),
        )
        + svg.text(
            inner,
            y + 78,
            big,
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 700),
        )
        + svg.text(
            inner,
            y + 100,
            sub,
            TextStyle(T.TYPE_SCALE["small"], _GOV, T.STACK_MONO, 500),
        )
        + svg.lines(
            inner,
            y + 134,
            svg.wrap("A binding law — break it and face enforcement and fines.", 48),
            20,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM),
        )
        + svg.text(
            inner,
            y + h - 46,
            (law if not law_missing else MISSING),
            TextStyle(13, T.TEXT, T.STACK_MONO, 500),
        )
        + svg.text(
            inner,
            y + h - 24,
            oid,
            TextStyle(T.TYPE_SCALE["small"], _GOV, T.STACK_MONO, 600),
        )
    )


def _india_side(r: RunResult, box: tuple[float, float, float, float]) -> str:
    x, y, w, h = box
    inner = x + 28
    big, sub = _modality_label(r.ai_security.regulatory.india_modality)
    principle, p_missing = svg.val(r.ai_security.regulatory.india_principle)
    oid, _ = svg.val(r.ai_security.regulatory.india_obligation_id)
    return (
        _gov_card(box, dashed=True)
        # outlined header = advisory/self-certified (deliberately not filled)
        + f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="{T.RADIUS}" '
        f'fill="none" stroke="{_GOV}" stroke-dasharray="7 5"/>'
        + svg.text(
            inner,
            y + 23,
            "INDIA",
            TextStyle(T.TYPE_SCALE["eyebrow"], _GOV, T.STACK_MONO, 700, spacing=2),
        )
        + svg.text(
            inner,
            y + 78,
            big,
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 700),
        )
        + svg.text(
            inner,
            y + 100,
            sub,
            TextStyle(T.TYPE_SCALE["small"], _GOV, T.STACK_MONO, 500),
        )
        + svg.lines(
            inner,
            y + 134,
            svg.wrap(
                "Principles you certify you uphold — a deliberate, innovation-"
                "preserving choice, and the harder thing to build software for.",
                48,
            ),
            20,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM),
        )
        + svg.text(
            inner,
            y + h - 46,
            (principle if not p_missing else MISSING),
            TextStyle(13, T.TEXT, T.STACK_MONO, 500),
        )
        + svg.text(
            inner,
            y + h - 24,
            oid,
            TextStyle(T.TYPE_SCALE["small"], _GOV, T.STACK_MONO, 600),
        )
    )


def _governance_band(r: RunResult) -> str:
    top, h = 304.0, 248.0
    eu_box = (64.0, top, 552.0, h)
    in_box = (664.0, top, 552.0, h)
    # the SAME risk forks down into two regimes — drawn from the shared-risk strip's
    # bottom corners into each card (a deliberate fork = the fragmentation).
    conn = (
        f'<path d="M640 238 L640 274 L340 274 L340 {top}" fill="none" '
        f'stroke="{_GOV}" stroke-width="1.5" stroke-opacity="0.6" stroke-dasharray="6 5"/>'
        f'<path d="M640 238 L640 274 L940 274 L940 {top}" fill="none" '
        f'stroke="{_GOV}" stroke-width="1.5" stroke-opacity="0.6" stroke-dasharray="6 5"/>'
        f'<circle cx="640" cy="238" r="4" fill="{_RISK}"/>'
    )
    return (
        svg.text(
            _VIEWBOX_W / 2,
            282,
            "ONE RISK · TWO RULEBOOKS — the same risk, governed two different ways",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], T.TEXT_DIM, T.STACK_MONO, 600, "middle", 2
            ),
        )
        + conn
        + _eu_side(r, eu_box)
        + _india_side(r, in_box)
    )


# --- band 2: one report, every regulator (formats) ---------------------------


def _format_card(
    box: tuple[float, float, float, float],
    title: str,
    sub: str,
    rows: list[tuple[str, str]],
) -> str:
    x, y, w, h = box
    inner = x + 28
    head = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{_OURS_WASH}" stroke="{_OURS}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="3" height="{h}" rx="1.5" fill="{_OURS}"/>'
        + svg.text(
            inner,
            y + 32,
            title,
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT, T.STACK_DISPLAY, 700),
        )
        + svg.text(
            inner,
            y + 54,
            sub,
            TextStyle(T.TYPE_SCALE["small"], _OURS, T.STACK_MONO, 500),
        )
        + f'<line x1="{inner}" y1="{y + 70}" x2="{x + w - 28}" y2="{y + 70}" stroke="{T.HAIRLINE}"/>'
    )
    # each row: real field NAME (mono, dim) : value (mono, bright) — the "shape"
    body = "".join(
        svg.text(
            inner,
            y + 98 + i * 30,
            f"{name}",
            TextStyle(12, T.TEXT_DIM, T.STACK_MONO, 500),
        )
        + svg.text(
            inner + 250,
            y + 98 + i * 30,
            value,
            TextStyle(13, T.TEXT, T.STACK_MONO, 600, "end"),
        )
        for i, (name, value) in enumerate(rows)
    )
    return head + body


def _finnet_rows(r: RunResult) -> list[tuple[str, str]]:
    f = r.report.finnet
    tx0 = _get(f, "suspicious_transactions", 0) or {}
    return [
        ("report_type", svg.val(_get(f, "report_type"))[0]),
        ("ground_of_suspicion", svg.val(_get(f, "ground_of_suspicion"))[0]),
        ("transaction_id", svg.val(_get(tx0, "transaction_id"))[0]),
        ("amount", svg.val(_get(tx0, "amount"))[0]),
        ("total_amount", svg.val(_get(f, "total_amount"))[0]),
    ]


def _goaml_rows(r: RunResult) -> list[tuple[str, str]]:
    g = r.report.goaml
    tx0 = _get(g, "transactions", 0) or {}
    txns = _get(g, "transactions")
    count = str(len(txns)) if isinstance(txns, list) else MISSING
    return [
        ("report_code", svg.val(_get(g, "report_code"))[0]),
        ("report_indicator", svg.val(_get(g, "report_indicator"))[0]),
        ("transactionnumber", svg.val(_get(tx0, "transactionnumber"))[0]),
        ("amount_local", svg.val(_get(tx0, "amount_local"))[0]),
        ("transactions", count),
    ]


def _formats_band(r: RunResult) -> str:
    typ, _ = svg.val(r.financial_crime.typology)
    total = svg.money(r.report.total_amount, r.report.currency)
    n = r.report.transaction_count
    node_x, node_y, node_w, node_h = 470.0, 636.0, 340.0, 60.0
    node_cx = node_x + node_w / 2
    top = 724.0
    fan = "".join(
        f'<line x1="{node_cx}" y1="{node_y + node_h}" x2="{cx}" y2="{top}" '
        f'stroke="{_OURS}" stroke-width="2" stroke-opacity="0.7"/>'
        for cx in (340.0, 940.0)
    )
    node = (
        f'<rect x="{node_x}" y="{node_y}" width="{node_w}" height="{node_h}" rx="{T.RADIUS}" '
        f'fill="{_OURS_WASH}" stroke="{_OURS}" stroke-width="1.5"/>'
        + svg.text(
            node_cx,
            node_y + 26,
            "ONE SIGNED STR · ONE FACT MODEL",
            TextStyle(T.TYPE_SCALE["eyebrow"], _OURS, T.STACK_MONO, 600, "middle", 1.5),
        )
        + svg.text(
            node_cx,
            node_y + 48,
            f"FATF {typ} · {n} tx · {total}",
            TextStyle(13, T.TEXT, T.STACK_MONO, 600, "middle"),
        )
    )
    finnet = _format_card(
        (64.0, top, 552.0, 250.0),
        "FINnet 2.0 — FIU-IND",
        "INDIA · the primary filing",
        _finnet_rows(r),
    )
    goaml = _format_card(
        (664.0, top, 552.0, 250.0),
        "goAML — UN",
        "70+ COUNTRIES · the same facts",
        _goaml_rows(r),
    )
    return (
        svg.text(
            _VIEWBOX_W / 2,
            612,
            "ONE REPORT · EVERY REGULATOR — same facts, any format (pluggable)",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], T.TEXT_DIM, T.STACK_MONO, 600, "middle", 2
            ),
        )
        + fan
        + node
        + finnet
        + goaml
    )


def _takeaway() -> str:
    return svg.text(
        _VIEWBOX_W / 2,
        994,
        "One system that speaks every jurisdiction's language — built for the "
        "harder, more common reality.",
        TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT, T.STACK_DISPLAY, 600, "middle"),
    )


def _footer(r: RunResult) -> str:
    reg = r.ai_security.regulatory
    chain = "verified" if r.arc.chain_verified else "TAMPERED"
    color = _OURS if r.arc.chain_verified else T.BERRY
    y = _VIEWBOX_H - 28
    right = f"chain {chain} · {r.arc.entry_count} entries"
    dot_x = _VIEWBOX_W - 64 - 8.4 * len(right) - 14
    return (
        f'<line x1="64" y1="{y - 24}" x2="{_VIEWBOX_W - 64}" y2="{y - 24}" stroke="{T.HAIRLINE}"/>'
        + svg.text(
            64,
            y,
            f"Rendered from a real run · {reg.eu_obligation_id} ({reg.eu_modality}) "
            f"· {reg.india_obligation_id} ({reg.india_modality})",
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO),
        )
        + f'<circle cx="{dot_x:.1f}" cy="{y - 4}" r="4" fill="{color}"/>'
        + svg.text(
            _VIEWBOX_W - 64,
            y,
            right,
            TextStyle(
                T.TYPE_SCALE["small"],
                T.TEXT_DIM if r.arc.chain_verified else color,
                T.STACK_MONO,
                anchor="end",
            ),
        )
    )


def _empty_state(message: str) -> str:
    cx, cy = _VIEWBOX_W / 2, _VIEWBOX_H / 2
    body = (
        svg.text(
            cx,
            cy - 16,
            "No run to show",
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600, "middle"),
        )
        + svg.text(
            cx,
            cy + 16,
            message,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, anchor="middle"),
        )
        + svg.text(
            cx,
            cy + 52,
            "▮▮▮▮▮   ▮▮▮▮▮",
            TextStyle(
                T.TYPE_SCALE["data"], T.MUTED, T.STACK_MONO, anchor="middle", spacing=4
            ),
        )
    )
    return svg.document(body, width=_VIEWBOX_W, height=_VIEWBOX_H, label=_LABEL)


def jurisdiction_svg(result: RunResult | None) -> str:
    """The jurisdiction hero as a self-contained SVG string (or empty state)."""
    if result is None:
        return _empty_state("Run the demo or load a saved run to render the contrast.")
    body = (
        _header()
        + _shared_risk(result)
        + _governance_band(result)
        + _formats_band(result)
        + _takeaway()
        + _footer(result)
    )
    return svg.document(body, width=_VIEWBOX_W, height=_VIEWBOX_H, label=_LABEL)


def jurisdiction_html(result: RunResult | None) -> str:
    """The SVG wrapped for `components.v1.html` — fonts + a centred container."""
    return (
        f"<style>{T.fonts_css()}html,body{{margin:0;background:{T.INK};}}"
        f".ks-juris{{max-width:{_HERO_MAX_WIDTH}px;margin:0 auto;}}</style>"
        f'<div class="ks-juris">{jurisdiction_svg(result)}</div>'
    )
