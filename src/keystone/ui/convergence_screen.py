"""The convergence hero (M2-0n) — the loop made visible: violated → satisfied.

The fourth sibling of the seam / jurisdiction / matrix heroes, and Movement 2's payoff —
the SEQUEL to the seam hero (same TXN-000016 throughline). Where the seam showed "one
event, two failures", this shows the THIRD beat: that same event IS the audit evidence
that takes a named regulatory obligation from VIOLATED to SATISFIED — across EU hard law
and India's advisory regime.

The motion is a TEMPORAL STATE-FLIP (a different motion than the matrix's convergence,
fitting a different claim, same forensic aesthetic):

- CENTRE (one transition, deep): the strongest hard-law obligation shown VIOLATED →
  SATISFIED, with the assurance before/after (10/12 → 0/12) as the VISIBLE CAUSE of the
  flip — the SAME 10→0 that hardens the AI is the cause that satisfies the control, one
  motion. The mapping's reason (the defensible link) + citation + modality are shown.
- STRIP (the rest, compact — breadth + the cross-jurisdiction spread): the other
  evidenced mappings as compact entries, each tagged jurisdiction + modality, with their
  own violated→satisfied state. One-deep-rest-compact (the matrix-screen discipline).
- BOUNDARY: the DPDP mapping shown (like P4) as a DELIBERATE "not evidenced by this
  event" entry — equal dignity, a distinct dashed treatment, the principled reason shown.
- DISCLAIMER: the honest framing ON the screen (a credibility asset, not a hedge) —
  Keystone shows the evidence relationship; a qualified auditor makes the determination.

Every value is read from `RunResult.convergence` (derived from REGISTERED_MAPPINGS) —
never hardcoded. Colour/type/spacing from `keystone.ui.tokens`; pure string building.
"""

from __future__ import annotations

from keystone.demo import ConvergenceMappingView, RunResult

from . import tokens as T
from .svg import MISSING, TextStyle, document
from .svg import lines as _lines
from .svg import text as _text
from .svg import val as _val
from .svg import wrap as _wrap

_VIEWBOX_W = 1280
_VIEWBOX_H = 900
_HERO_MAX_WIDTH = 1180
CONVERGENCE_HEIGHT_PX = round(_HERO_MAX_WIDTH * _VIEWBOX_H / _VIEWBOX_W) + 18

_LABEL = "Regulatory convergence: the same event, violated then satisfied"

# The locked on-screen framing of the disclaimer (a credibility asset, not a hedge).
_DISCLAIMER_LEAD = (
    "Keystone shows the evidence relationship; a qualified auditor makes the "
    "compliance determination."
)


def _svg_document(body: str) -> str:
    return document(body, width=_VIEWBOX_W, height=_VIEWBOX_H, label=_LABEL)


def _short(label: str) -> tuple[str, str]:
    """Split an obligation label 'INSTRUMENT · PROVISION — TITLE' into (heading, title)."""
    head, _, title = label.partition(" — ")
    return head, title


def _clamp(rows: list[str], limit: int) -> list[str]:
    """Cap wrapped text to `limit` lines (compact cards), marking truncation with an ellipsis."""
    if len(rows) <= limit:
        return rows
    kept = rows[:limit]
    kept[-1] = kept[-1].rstrip(".,") + " …"
    return kept


def _empty_state(message: str) -> str:
    cx, cy = _VIEWBOX_W / 2, _VIEWBOX_H / 2
    return _svg_document(
        _text(
            cx,
            cy - 16,
            "No convergence to show",
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 600, "middle"),
        )
        + _text(
            cx,
            cy + 16,
            message,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM, anchor="middle"),
        )
    )


def _header(r: RunResult) -> str:
    c = r.convergence
    tx = _val(r.binding.transaction_id)[0]
    summary = (
        f"{c.evidenced_count} obligations evidenced · {c.hard_law_count} hard-law / "
        f"{c.advisory_count} advisory · {c.boundary_count} boundary"
    )
    return (
        f'<circle cx="52" cy="52" r="4" fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            68,
            56,
            "KEYSTONE · REGULATORY CONVERGENCE",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], T.NVIDIA_GREEN, T.STACK_MONO, 600, spacing=1.6
            ),
        )
        + _text(
            48,
            104,
            "The same event. Violated, then satisfied.",
            TextStyle(T.TYPE_SCALE["hero"], T.TEXT, T.STACK_DISPLAY, 700, spacing=-0.5),
        )
        + _text(
            48,
            134,
            "The attack the red-team found IS the audit evidence that takes a regulatory "
            "obligation from violated to satisfied — across EU hard law and India advisory.",
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT_DIM),
        )
        + _text(
            48,
            158,
            f"Same event — {tx} — the seam's third beat.",
            TextStyle(T.TYPE_SCALE["small"], T.AMBER, T.STACK_MONO, 500, spacing=0.5),
        )
        + _text(
            _VIEWBOX_W - 48,
            158,
            summary,
            TextStyle(T.TYPE_SCALE["small"], T.AMBER, T.STACK_MONO, 600, "end", 0.5),
        )
    )


def _state_box(
    box: tuple[float, float, float, float],
    color: str,
    parts: tuple[str, str, str, str],
) -> str:
    x, y, w, h = box
    cx = x + w / 2
    tag, big, unit, verdict = parts
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.PANEL}" stroke="{color}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{y}" width="3" height="{h}" rx="1.5" fill="{color}"/>'
        + _text(
            cx + 2,
            y + 30,
            tag,
            TextStyle(T.TYPE_SCALE["eyebrow"], color, T.STACK_MONO, 600, "middle", 1.5),
        )
        + _text(
            cx + 2, y + 88, big, TextStyle(48, T.TEXT, T.STACK_DISPLAY, 700, "middle")
        )
        + _text(
            cx + 2,
            y + 112,
            unit,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO, anchor="middle"),
        )
        + _lines(
            cx + 2,
            y + 142,
            _wrap(verdict, 34),
            16,
            TextStyle(T.TYPE_SCALE["small"], color, T.STACK_DISPLAY, 600, "middle"),
        )
    )


def _centre(m: ConvergenceMappingView, top: float) -> str:
    """The deep one: the strongest hard-law obligation, violated → satisfied, 10→0 the cause."""
    x, w, h = 64.0, 1152.0, 348.0
    inner = x + 28
    head, title = _short(m.obligation_label)
    cap = m.prompt_cap or 12
    bx, bw, bh = 110.0, 430.0, 150.0
    box_y = top + 96
    body = (
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.AMBER_PANEL}" stroke="{T.AMBER}" stroke-width="1.5"/>'
        f'<rect x="{x}" y="{top}" width="{w}" height="3" rx="1.5" fill="{T.AMBER}"/>'
        + _text(
            inner,
            top + 30,
            "THE STRONGEST CASE · HARD LAW",
            TextStyle(T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, spacing=1.6),
        )
        + _text(
            inner,
            top + 60,
            head,
            TextStyle(T.TYPE_SCALE["title"], T.TEXT, T.STACK_DISPLAY, 700),
        )
        + _text(
            inner,
            top + 82,
            title,
            TextStyle(T.TYPE_SCALE["body"], T.TEXT_DIM),
        )
        + _text(
            x + w - 28,
            top + 34,
            f"{m.jurisdiction} · {m.modality_label.upper()}",
            TextStyle(T.TYPE_SCALE["small"], T.AMBER, T.STACK_MONO, 600, "end", 1),
        )
        + _text(
            x + w - 28,
            top + 56,
            m.obligation_id,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO, anchor="end"),
        )
        # the state-flip = the assurance before/after, made the cause
        + _state_box(
            (bx, box_y, bw, bh),
            T.BERRY,
            (
                "VIOLATED · BEFORE THE PATCH",
                f"{m.before_fails} / {cap}",
                "probes exploited the agent",
                "✗ the obligation was violated",
            ),
        )
        + _state_box(
            (x + w - bw - 46, box_y, bw, bh),
            T.NVIDIA_GREEN,
            (
                "SATISFIED · AFTER THE PATCH",
                f"{m.after_fails} / {cap}",
                "probes exploited the agent",
                "✓ the control demonstrated",
            ),
        )
    )
    # the arrow + the "one motion" caption between the boxes
    ax_l = bx + bw
    ax_r = x + w - bw - 46
    ay = box_y + bh / 2
    body += (
        f'<line x1="{ax_l + 8}" y1="{ay}" x2="{ax_r - 16}" y2="{ay}" '
        f'stroke="{T.NVIDIA_GREEN}" stroke-width="2"/>'
        f'<path d="M{ax_r - 24} {ay - 7} L{ax_r - 8} {ay} L{ax_r - 24} {ay + 7} Z" '
        f'fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            (ax_l + ax_r) / 2,
            ay - 16,
            f"{m.before_fails} → {m.after_fails}",
            TextStyle(
                T.TYPE_SCALE["body"], T.NVIDIA_GREEN, T.STACK_MONO, 700, "middle"
            ),
        )
        + _lines(
            (ax_l + ax_r) / 2,
            ay + 22,
            _wrap("the assurance loop that hardens the AI", 18),
            15,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_MONO, 500, "middle"),
        )
    )
    # the reason (the defensible link)
    body += _text(
        inner,
        top + 264,
        "WHY THIS EVENT IS THE EVIDENCE",
        TextStyle(T.TYPE_SCALE["eyebrow"], T.TEXT_DIM, T.STACK_MONO, 600, spacing=1.2),
    ) + _lines(
        inner,
        top + 286,
        _wrap(m.reason or MISSING, 124),
        17,
        TextStyle(T.TYPE_SCALE["small"], T.TEXT, T.STACK_BODY),
    )
    return body


def _strip_card(m: ConvergenceMappingView, x: float, top: float, w: float) -> str:
    """A compact entry: an evidenced obligation (violated→satisfied) or the boundary."""
    h = 232.0
    inner = x + 22
    head, title = _short(m.obligation_label)
    if m.kind == "NOT_EVIDENCED":
        return (
            f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="{T.RADIUS}" '
            f'fill="{T.AMBER_WASH}" stroke="{T.AMBER}" stroke-width="1.5" '
            f'stroke-dasharray="7 5"/>'
            + _text(
                inner,
                top + 28,
                "BOUNDARY · NOT EVIDENCED",
                TextStyle(
                    T.TYPE_SCALE["eyebrow"], T.AMBER, T.STACK_MONO, 600, spacing=1
                ),
            )
            + _text(
                inner,
                top + 54,
                head,
                TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT, T.STACK_DISPLAY, 600),
            )
            + _text(
                inner,
                top + 74,
                f"{m.jurisdiction} · {m.modality_label} · {m.obligation_id}",
                TextStyle(T.TYPE_SCALE["small"], T.AMBER, T.STACK_MONO, 500),
            )
            + _lines(
                inner,
                top + 104,
                _clamp(_wrap(m.reason or MISSING, 40), 7),
                16,
                TextStyle(T.TYPE_SCALE["small"], "#E7B973", T.STACK_BODY, 500),
            )
        )
    return (
        f'<rect x="{x}" y="{top}" width="{w}" height="{h}" rx="{T.RADIUS}" '
        f'fill="{T.PANEL}" stroke="{T.HAIRLINE}"/>'
        f'<rect x="{x}" y="{top}" width="3" height="{h}" rx="1.5" fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            inner,
            top + 28,
            "EVIDENCED · VIOLATED → SATISFIED",
            TextStyle(
                T.TYPE_SCALE["eyebrow"], T.NVIDIA_GREEN, T.STACK_MONO, 600, spacing=1
            ),
        )
        + _text(
            inner,
            top + 54,
            head,
            TextStyle(T.TYPE_SCALE["subtitle"], T.TEXT, T.STACK_DISPLAY, 600),
        )
        + _lines(
            inner,
            top + 76,
            _wrap(title, 40),
            16,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT_DIM, T.STACK_BODY),
        )
        + _text(
            inner,
            top + 128,
            f"{m.jurisdiction} · {m.modality_label.upper()}",
            TextStyle(T.TYPE_SCALE["small"], T.AMBER, T.STACK_MONO, 600, spacing=0.8),
        )
        # the mini state-flip
        + _text(
            inner,
            top + 162,
            "VIOLATED",
            TextStyle(T.TYPE_SCALE["small"], T.BERRY, T.STACK_MONO, 600),
        )
        + _text(
            inner + 78,
            top + 162,
            "→",
            TextStyle(T.TYPE_SCALE["body"], T.NVIDIA_GREEN, T.STACK_MONO, 700),
        )
        + _text(
            inner + 100,
            top + 162,
            "SATISFIED",
            TextStyle(T.TYPE_SCALE["small"], T.NVIDIA_GREEN, T.STACK_MONO, 600),
        )
        + _text(
            inner,
            top + 190,
            f"{m.before_fails}/{m.prompt_cap} → {m.after_fails}/{m.prompt_cap} probes · "
            f"{m.obligation_id}",
            TextStyle(T.TYPE_SCALE["small"], T.MUTED, T.STACK_MONO, 500),
        )
    )


def _footer(r: RunResult) -> str:
    y = _VIEWBOX_H - 58
    return (
        f'<line x1="48" y1="{y - 18}" x2="{_VIEWBOX_W - 48}" y2="{y - 18}" stroke="{T.HAIRLINE}"/>'
        + f'<rect x="48" y="{y - 6}" width="3" height="36" rx="1.5" fill="{T.NVIDIA_GREEN}"/>'
        + _text(
            66,
            y + 6,
            _DISCLAIMER_LEAD,
            TextStyle(T.TYPE_SCALE["small"], T.TEXT, T.STACK_DISPLAY, 600),
        )
        + _lines(
            66,
            y + 26,
            _wrap(r.convergence.disclaimer or MISSING, 150),
            15,
            TextStyle(10, T.TEXT_DIM, T.STACK_BODY),
        )
        + _text(
            _VIEWBOX_W - 48,
            _VIEWBOX_H - 22,
            "Derived from REGISTERED_MAPPINGS · nothing hardcoded",
            TextStyle(T.TYPE_SCALE["small"], T.MUTED, T.STACK_MONO, anchor="end"),
        )
    )


def convergence_svg(result: RunResult | None) -> str:
    """The convergence hero as a self-contained SVG string, from a `RunResult`."""
    if result is None or not result.convergence.mappings:
        return _empty_state(
            "Run the demo or load a saved run to render the convergence."
        )

    mappings = result.convergence.mappings
    evidenced = [m for m in mappings if m.kind == "EVIDENCED"]
    boundaries = [m for m in mappings if m.kind == "NOT_EVIDENCED"]
    if not evidenced:
        return _empty_state("No evidenced obligations in this run.")

    # The centre = the strongest hard-law evidenced mapping (derived, not hardcoded).
    primary = next((m for m in evidenced if m.modality == "HARD_LAW"), evidenced[0])
    rest = [m for m in evidenced if m is not primary]
    strip = [*rest, *boundaries]

    body = _header(result) + _centre(primary, 186.0)

    # strip: one-deep-rest-compact, derived from the remaining mappings.
    strip_top = 560.0
    gap = 24.0
    count = max(len(strip), 1)
    card_w = (1152.0 - gap * (count - 1)) / count
    for i, m in enumerate(strip):
        body += _strip_card(m, 64.0 + i * (card_w + gap), strip_top, card_w)

    body += _footer(result)
    return _svg_document(body)


def convergence_html(result: RunResult | None) -> str:
    """A self-contained HTML doc for `components.v1.html` (an iframe), centred on ink."""
    return (
        f"<style>{T.fonts_css()}"
        f"html,body{{margin:0;background:{T.INK};}}"
        f".ks-conv{{max-width:{_HERO_MAX_WIDTH}px;margin:0 auto;}}</style>"
        f'<div class="ks-conv">{convergence_svg(result)}</div>'
    )
