"""The three supporting views for the KS-0503 shell — the frame around the heroes.

Quiet by design (the heroes spent the boldness): the evidence ledger, the cross-layer
posture, and the assurance before/after. All built on the shared `keystone.ui.svg`
vocabulary + `keystone.ui.tokens`, so the whole app reads as one product. Every value
comes from the `keystone.demo.RunResult` (v3); a missing field shows ▮ and a missing
run shows an honest empty state.
"""

from __future__ import annotations

from keystone.core.ledger import LedgerEntry
from keystone.demo import RunResult

from . import svg
from . import tokens as T
from .svg import MISSING, TextStyle

_W = 1280
_HERO_MAX_WIDTH = 1180

# viewBox heights per view; iframe px heights derive from them (never clip).
LEDGER_H = 612
POSTURE_H = 556
BEFORE_AFTER_H = 520


def _px(view_h: int) -> int:
    return round(_HERO_MAX_WIDTH * view_h / _W) + 18


LEDGER_HEIGHT_PX = _px(LEDGER_H)
POSTURE_HEIGHT_PX = _px(POSTURE_H)
BEFORE_AFTER_HEIGHT_PX = _px(BEFORE_AFTER_H)

# Plain-language description for each Layer-1 arc stage (the no-one-confused rule).
_STAGE_PLAIN: dict[str, str] = {
    "ingested": "the synthetic transaction stream, including the seam transfer",
    "detected": "memo-blind FATF flags the structuring cluster on amounts & timing",
    "seam_bound": "the flagged transfer is shown to carry the L2 vulnerability signature",
    "reported": "a FINnet STR is drafted with a guarded narrative",
    "signed": "human sign-off — the report moves draft → signed",
}


def _header(eyebrow: str, title: str, subtitle: str) -> str:
    return (
        svg.pill(64, 56, eyebrow, T.NVIDIA_GREEN)
        + svg.text(
            64,
            100,
            title,
            TextStyle(
                T.TYPE_SCALE["title"] + 6, T.TEXT, T.STACK_DISPLAY, 700, spacing=-0.3
            ),
        )
        + svg.text(64, 128, subtitle, TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM))
    )


def _empty(view_h: int, label: str, message: str) -> str:
    cx, cy = _W / 2, view_h / 2
    body = svg.text(
        cx,
        cy - 8,
        "No run to show",
        TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600, "middle"),
    ) + svg.text(
        cx,
        cy + 20,
        message,
        TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, anchor="middle"),
    )
    return svg.document(body, width=_W, height=view_h, label=label)


# --- evidence ledger ----------------------------------------------------------


def ledger_svg(result: RunResult | None) -> str:
    if result is None:
        return _empty(
            LEDGER_H, "Evidence ledger", "Run or load a run to see the ledger."
        )
    arc = result.arc
    entries: tuple[LedgerEntry, ...] = arc.entries
    rows = []
    top = 176
    for i, stage in enumerate(arc.stages):
        y = top + i * 62
        entry = entries[i] if i < len(entries) else None
        ledger_id = f"#{entry.id}" if entry else MISSING
        digest = entry.entry_hash[:10] if entry else MISSING
        rows.append(
            svg.text(
                64,
                y,
                f"{i + 1:02d}",
                TextStyle(T.TYPE_SCALE["data"], T.NVIDIA_GREEN, T.STACK_MONO, 600),
            )
            + svg.text(
                104,
                y,
                stage.replace("_", " ").upper(),
                TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT, T.STACK_DISPLAY, 600),
            )
            + svg.text(
                104,
                y + 22,
                _STAGE_PLAIN.get(stage, stage),
                TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM),
            )
            + svg.text(
                _W - 64,
                y,
                f"entry {ledger_id}",
                TextStyle(
                    T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO, anchor="end"
                ),
            )
            + svg.text(
                _W - 64,
                y + 20,
                digest,
                TextStyle(T.TYPE_SCALE["small"], T.MUTED, T.STACK_MONO, anchor="end"),
            )
            + f'<line x1="64" y1="{y + 34}" x2="{_W - 64}" y2="{y + 34}" stroke="{T.HAIRLINE}"/>'
        )
    chain = "verified" if arc.chain_verified else "TAMPERED"
    color = T.NVIDIA_GREEN if arc.chain_verified else T.BERRY
    badge_y = top + len(arc.stages) * 62 + 18
    badge = f'<circle cx="68" cy="{badge_y - 4}" r="5" fill="{color}"/>' + svg.text(
        84,
        badge_y,
        f"chain {chain} · {arc.entry_count} entries · tamper-evident "
        "(each entry hashes the previous)",
        TextStyle(
            T.TYPE_SCALE["body"],
            color if not arc.chain_verified else T.TEXT,
            T.STACK_MONO,
            500,
        ),
    )
    body = (
        _header(
            "EVIDENCE LEDGER · AUDITABLE BY CONSTRUCTION",
            "The hash-chained evidence trail",
            "Every step is appended as a tamper-evident entry; the chain re-verifies on load.",
        )
        + "".join(rows)
        + badge
    )
    return svg.document(body, width=_W, height=LEDGER_H, label="Evidence ledger")


# --- cross-layer posture ------------------------------------------------------


def _posture_card(
    box: tuple[float, float, float, float],
    color: str,
    head: tuple[str, str],
    rows: list[str],
) -> str:
    x, y, w, h = box
    tag, title = head
    inner = x + 26
    body = (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.PANEL}" stroke="{color}" stroke-opacity="0.55"/>'
        f'<rect x="{x}" y="{y}" width="3" height="{h}" rx="1.5" fill="{color}"/>'
        + svg.pill(inner, y + 34, tag, color)
        + svg.text(
            inner,
            y + 74,
            title,
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT, T.STACK_DISPLAY, 600),
        )
        + f'<line x1="{inner}" y1="{y + 90}" x2="{x + w - 26}" y2="{y + 90}" stroke="{T.HAIRLINE}"/>'
    )
    for i, row in enumerate(rows):
        body += svg.lines(
            inner,
            y + 118 + i * 40,
            svg.wrap(row, 34),
            18,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO, 500),
        )
    return body


def posture_svg(result: RunResult | None) -> str:
    if result is None:
        return _empty(
            POSTURE_H, "Cross-layer posture", "Run or load a run to see posture."
        )
    reg = result.ai_security.regulatory
    a = result.ai_security.assurance
    fc = result.financial_crime
    rep = result.report
    top, h, w = 176.0, 300.0, 368.0
    l3 = _posture_card(
        (64.0, top, w, h),
        T.TEAL,
        ("LAYER 3 · OBLIGATIONS", "Rules it must satisfy"),
        [
            f"EU: {svg.val(reg.eu_ai_act)[0]}",
            f"  {reg.eu_obligation_id} · {reg.eu_modality}",
            f"India: {svg.val(reg.india_principle)[0]}",
            f"  {reg.india_obligation_id} · {reg.india_modality}",
        ],
    )
    l2 = _posture_card(
        (468.0, top, w, h),
        T.PURPLE,
        ("LAYER 2 · AI ASSURANCE", "Vulnerability found & patched"),
        [
            f"signature: {svg.val(result.ai_security.signature_name)[0]}",
            "Garak found → Guardrails patched",
            f"probes: {a.before_fails}/{a.prompt_cap} → {a.after_fails}/{a.prompt_cap}",
            "the AI agent was hardened",
        ],
    )
    l1 = _posture_card(
        (872.0, top, w, h),
        T.BERRY,
        ("LAYER 1 · FINANCIAL CRIME", "Fraud caught & reported"),
        [
            f"FATF {svg.val(fc.typology)[0]} · {svg.val(fc.severity)[0]}",
            f"STR {rep.status} · {rep.report_format} + goAML",
            f"total {svg.money(rep.total_amount, rep.currency)}",
            "the crime was filed",
        ],
    )
    body = (
        _header(
            "CROSS-LAYER POSTURE · WHOLE-SYSTEM STATE",
            "All three layers, one verifiable run",
            "Obligations mapped, the AI hardened, the crime caught and filed — at a glance.",
        )
        + l3
        + l2
        + l1
        + svg.text(
            _W / 2,
            top + h + 40,
            "One transaction moved through every layer — and left a verifiable trail.",
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, T.STACK_DISPLAY, 500, "middle"),
        )
    )
    return svg.document(body, width=_W, height=POSTURE_H, label="Cross-layer posture")


# --- assurance before / after -------------------------------------------------


def _ba_panel(
    box: tuple[float, float, float, float], color: str, parts: tuple[str, str, str, str]
) -> str:
    x, y, w, h = box
    cx = x + w / 2
    tag, big, unit, verdict = parts
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.PANEL}" stroke="{color}" stroke-width="1.5"/>'
        + svg.text(
            cx,
            y + 38,
            tag,
            TextStyle(T.TYPE_SCALE["eyebrow"], color, T.STACK_MONO, 600, "middle", 2),
        )
        + svg.text(
            cx, y + 130, big, TextStyle(76, T.TEXT, T.STACK_DISPLAY, 700, "middle")
        )
        + svg.text(
            cx,
            y + 162,
            unit,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, T.STACK_MONO, anchor="middle"),
        )
        + svg.text(
            cx,
            y + 210,
            verdict,
            TextStyle(T.TYPE_SCALE["subtitle"], color, T.STACK_DISPLAY, 600, "middle"),
        )
    )


def before_after_svg(result: RunResult | None) -> str:
    if result is None:
        return _empty(
            BEFORE_AFTER_H, "Assurance before/after", "Run or load a run to see it."
        )
    a = result.ai_security.assurance
    top, h, w = 188.0, 244.0, 472.0
    before = _ba_panel(
        (64.0, top, w, h),
        T.BERRY,
        (
            "UNGUARDED",
            f"{a.before_fails} / {a.prompt_cap}",
            "prompt-injection probes exploited the agent",
            "✗ unauthorized transfer fired" if a.exploit_before else "✗ exploited",
        ),
    )
    after = _ba_panel(
        (744.0, top, w, h),
        T.NVIDIA_GREEN,
        (
            "WITH THE GUARDRAILS RAIL",
            f"{a.after_fails} / {a.prompt_cap}",
            "probes exploited the agent",
            "✓ blocked by Guardrails" if not a.exploit_after else "✗ still exploited",
        ),
    )
    arrow_y = top + h / 2
    arrow = (
        f'<line x1="544" y1="{arrow_y}" x2="736" y2="{arrow_y}" stroke="{T.NVIDIA_GREEN}" '
        f'stroke-width="2"/>'
        f'<path d="M728 {arrow_y - 7} L744 {arrow_y} L728 {arrow_y + 7} Z" fill="{T.NVIDIA_GREEN}"/>'
        + svg.text(
            640,
            arrow_y - 14,
            "patched",
            TextStyle(
                T.TYPE_SCALE["small"], T.NVIDIA_GREEN, T.STACK_MONO, 600, "middle"
            ),
        )
    )
    caption = svg.text(
        _W / 2,
        top + h + 46,
        f"{svg.val(a.found_by)[0]}  found the hole; {svg.val(a.patched_by)[0]} "
        "closed it — re-tested to zero.",
        TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, anchor="middle"),
    )
    body = (
        _header(
            "ASSURANCE · WE FOUND IT AND FIXED IT",
            "Red-teamed, then remediated",
            "An AI red-team found a prompt-injection hole; a Guardrails rail closed it.",
        )
        + before
        + arrow
        + after
        + caption
    )
    return svg.document(
        body, width=_W, height=BEFORE_AFTER_H, label="Assurance before/after"
    )


def view_html(svg_markup: str, *, max_width: int = _HERO_MAX_WIDTH) -> str:
    """Wrap a view's SVG for `components.v1.html` — fonts + a centred container."""
    return (
        f"<style>{T.fonts_css()}html,body{{margin:0;background:{T.INK};}}"
        f".ks-view{{max-width:{max_width}px;margin:0 auto;}}</style>"
        f'<div class="ks-view">{svg_markup}</div>'
    )
