"""Deterministic deontic (modal) strength classification — core, no LLM.

The *strength* of an obligation — binding ("shall"/"must") vs advisory
("should"/"may") — is a FACT, not a presentation choice, already encoded by
`enforcement_modality`. It is classified here deterministically so the LLM edge
(KS-0206 phrasing) can GUARD against modal drift: if a reworded summary changes
the modal force, the edge falls back to the authoritative curated summary.

Scope of protection (a CHOSEN line, not a gap — see MEMORY.md):
- The guard HARD-PROTECTS only (a) STRONG transitions — a STRONG source must not
  be presented as weaker, and an advisory source must not be pumped up to STRONG —
  and (b) HARD_LAW nodes reading advisory.
- Within-advisory drift (e.g. "should" <-> "may") on a non-hard-law node is
  treated as acceptable presentation latitude.

Asymmetric caution: a false fallback is harmless (the curated text is always a
safe answer); a missed weakening of a strong obligation is unacceptable. So when
a STRONG source's force cannot be confirmed in the phrasing, we fall back.
"""

from __future__ import annotations

import enum
import re

from keystone.core.obligations import Modality


class Tier(enum.IntEnum):
    """Modal strength tier. Ordered so the strongest marker present wins."""

    UNCLASSIFIED = 0
    WEAK = 1
    MEDIUM = 2
    STRONG = 3


# Tiered lexicon (word-boundary, case-insensitive). Conservative by design: the
# lexicon need not catch every nuance, but it must not MISS a weakening of a
# strong obligation. `\brequired\b` matches the verb/adjective but never the noun
# "requirement".
_STRONG = (
    r"\bshall\b",
    r"\bmust\b",
    r"\brequired\b",
    r"\brequired to\b",
    r"\bmandatory\b",
    r"\boblig\w+\b",
)
_MEDIUM = (
    r"\bshould\b",
    r"\bought to\b",
    r"\bexpected to\b",
    r"\brecommend\w*\b",
)
_WEAK = (
    r"\bmay\b",
    r"\bcan\b",
    r"\bencourag\w*\b",
    r"\boptional\b",
)
# Phrases that negate binding force — they signal advisory/non-binding and must
# NOT be read as STRONG (e.g. "not a binding direction", "not mandatory").
_NEGATED_BINDING = (
    "not binding",
    "non-binding",
    "not legally binding",
    "not mandatory",
    "not a binding",
    "not a mandatory",
)


def _strip_negated_binding(text: str) -> str:
    low = text.lower()
    for phrase in _NEGATED_BINDING:
        low = low.replace(phrase, " ")
    return low


def _has(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def classify(text: str) -> Tier:
    """Classify `text`'s operative modal strength as the highest tier present."""
    low = _strip_negated_binding(text)
    if _has(_STRONG, low):
        return Tier.STRONG
    if _has(_MEDIUM, low):
        return Tier.MEDIUM
    if _has(_WEAK, low):
        return Tier.WEAK
    return Tier.UNCLASSIFIED


def detect_modal_drift(
    source: str, phrased: str, enforcement_modality: Modality
) -> bool:
    """Return True if `phrased` drifts the modal force of `source` (=> fall back).

    Two protected conditions:
    1. STRONG transition: a STRONG source rendered non-STRONG (weakening, INCLUDING
       the uncertain case where `phrased` carries no modal verb at all), or a
       non-STRONG source pumped up to STRONG (strengthening). Expressed as the XOR
       of "is STRONG" on each side. Because this is checked FIRST, the
       both-UNCLASSIFIED pass-through below is only reachable when the source is
       non-STRONG — a STRONG source going unclassified always falls back here.
    2. HARD_LAW cross-check: a hard-law node whose phrasing reads advisory
       (MEDIUM/WEAK) drifts even if the source clause was not itself STRONG.

    Within-advisory drift on a non-hard-law node (e.g. "should" -> "may") is
    intentionally NOT flagged (chosen scope; see module docstring / MEMORY.md).
    """
    src = classify(source)
    phr = classify(phrased)

    if (src is Tier.STRONG) != (phr is Tier.STRONG):
        return True
    # HARD_LAW node whose phrasing reads advisory (independent of source tier).
    return enforcement_modality is Modality.HARD_LAW and phr in (
        Tier.MEDIUM,
        Tier.WEAK,
    )
