"""Deterministic deontic (modal) strength classification — core, no LLM.

The *strength* of an obligation — binding ("must"/"shall") vs advisory
("should"/"may") — is a FACT, not a presentation choice. It is classified here
deterministically so the LLM edge (KS-0204 phrasing) can GUARD against modal
drift: if a phrased summary strengthens or weakens the modal force relative to
the curated source text, the edge falls back to the authoritative summary.

Design notes:
- BINDING detection favours precision: only unambiguous modal verbs/phrases
  count, so a phrasing that loses binding force (e.g. "shall" -> "should") is
  detected. Ambiguous nouns like "requirement" are deliberately NOT counted.
- Negated-binding phrases ("not binding", "not mandatory", ...) are stripped
  first so they read as advisory, not binding.
- The guard errs toward fallback: when in doubt the certainly-faithful curated
  summary is shown, never a probably-faithful reword.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Unambiguous binding markers (modal verbs + verb phrases). Nouns/adjectives that
# are ambiguous out of context (e.g. "requirement") are intentionally excluded.
_BINDING = (
    r"\bmust\b",
    r"\bshall\b",
    r"\bmandatory\b",
    r"\brequired to\b",
    r"\boblig\w+\b",
)
_ADVISORY = (
    r"\bshould\b",
    r"\bmay\b",
    r"\brecommend\w*\b",
    r"\bencourag\w*\b",
    r"\badvisor\w*\b",
)
# Phrases that negate binding force — they signal advisory/non-binding and must
# not be counted as binding (e.g. "not a binding direction", "not mandatory").
_NEGATED_BINDING = (
    "not binding",
    "non-binding",
    "not legally binding",
    "not mandatory",
    "not a binding",
    "not a mandatory",
)


@dataclass(frozen=True)
class ModalProfile:
    """Counts of binding and advisory modal markers in a piece of text."""

    binding: int
    advisory: int


def _strip_negated_binding(text: str) -> str:
    low = text.lower()
    for phrase in _NEGATED_BINDING:
        low = low.replace(phrase, " ")
    return low


def modal_profile(text: str) -> ModalProfile:
    """Classify the modal force of `text` (deterministic; case-insensitive)."""
    low = _strip_negated_binding(text)
    binding = sum(len(re.findall(p, low)) for p in _BINDING)
    advisory = sum(len(re.findall(p, low)) for p in _ADVISORY)
    return ModalProfile(binding=binding, advisory=advisory)


def drifts(source: str, candidate: str) -> bool:
    """Return True if `candidate` changed modal force relative to `source`.

    Two drift directions, both faithfulness defects:
    - strengthening: `candidate` asserts binding force the `source` did not;
    - weakening: `source` was binding but `candidate` drops to purely advisory.
    """
    src = modal_profile(source)
    cand = modal_profile(candidate)
    strengthened = cand.binding > 0 and src.binding == 0
    weakened = src.binding > 0 and cand.binding == 0 and cand.advisory > 0
    return strengthened or weakened
